/* Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
   Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
   Copyright 2021 Eugene Molotov <https://github.com/em230418>
   License MIT (https://opensource.org/licenses/MIT). */
odoo.define("pos_wechat", function (require) {
    "use strict";

    require("pos_qr_scan");
    require("pos_qr_show");
    var rpc = require("web.rpc");
    var core = require("web.core");
    var models = require("point_of_sale.models");
    var Backbone = window.Backbone;
    const PaymentScreen = require("pos_qr_show.PaymentScreen");
    const Registries = require("point_of_sale.Registries");

    models.load_fields("pos.payment.method", ["wechat_method", "wechat_journal_id"]);

    var Wechat = Backbone.Model.extend({
        initialize: function (pos) {
            var self = this;
            this.pos = pos;
            core.bus.on("qr_scanned", this, function (value) {
                if (self.check_auth_code(value)) {
                    self.process_qr(value);
                }
            });
        },
        check_is_integer: function (value) {
            // Due to travis AssertionError: ('TypeError: undefined is not a function (evaluating "'Number.isInteger(code)')\n"
            return (
                (Number.isInteger && Number.isInteger(value)) ||
                (typeof value === "number" &&
                    isFinite(value) &&
                    Math.floor(value) === value)
            );
        },
        check_auth_code: function (value) {
            // TODO: do we need to integrate this with barcode.nomenclature?
            var code = Number(value);
            if (
                code &&
                this.check_is_integer(code) &&
                code.length === 18 &&
                code[0] === 1 &&
                code[1] >= 0 &&
                code[1] <= 5
            ) {
                return true;
            }
            return false;
        },
        process_qr: function (auth_code) {
            var order = this.pos.get_order();
            if (!order) {
                return;
            }
            // TODO: block order for editing
            this.micropay(auth_code, order);
        },
        micropay: function (auth_code, order) {
            /* Send request asynchronously */
            var self = this;

            var terminal_ref = "POS/" + self.pos.config.name;
            var pos_id = self.pos.config.id;

            var send_it = function () {
                return rpc.query({
                    model: "wechat.micropay",
                    method: "pos_create_from_qr",
                    kwargs: {
                        auth_code: auth_code,
                        pay_amount: order.get_due(),
                        order_ref: order.uid,
                        terminal_ref: terminal_ref,
                        journal_id: self.pos.micropay_journal_id,
                        pos_id: pos_id,
                    },
                });
            };

            var current_send_number = 0;
            return send_it().fail(function (error, e) {
                if (self.pos.debug) {
                    console.log(
                        "Wechat",
                        self.pos.config.name,
                        "failed request #" + current_send_number + ":",
                        error.message
                    );
                }
                self.pos.show_warning();
            });
        },
    });

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function () {
            var self = this;
            PosModelSuper.prototype.initialize.apply(this, arguments);
            this.wechat = new Wechat(this);

            this.bus.add_channel_callback("wechat", this.on_wechat, this);
            this.ready.then(function () {
                // Take out wechat micropay cashregister from cashregisters to avoid
                // rendering in payment screent
                const pm = self.hide_payment_method(function (r) {
                    return r.wechat_method === "micropay";
                });
                if (pm) {
                    self.micropay_journal_id = pm.wechat_journal_id[0];
                }
            });
        },
        scan_product: function (parsed_code) {
            // TODO: do we need to make this optional?
            var value = parsed_code.code;
            if (this.wechat.check_auth_code(value)) {
                this.wechat.process_qr(value);
                return true;
            }
            return PosModelSuper.prototype.scan_product.apply(this, arguments);
        },
        on_wechat: function (msg) {
            this.add_qr_payment(
                msg.order_ref,
                msg.journal_id,
                msg.total_fee / 100.0,
                {
                    micropay_id: msg.micropay_id,
                },
                // Auto validate payment
                true
            );
        },
        wechat_qr_payment: function (order, pm) {
            /* Send request asynchronously */
            var self = this;

            var pos = this;
            var terminal_ref = "POS/" + pos.config.name;
            var pos_id = pos.config.id;

            var lines = order.orderlines.map(function (r) {
                return {
                    // Always use 1 because quantity is taken into account in price field
                    quantity: 1,
                    quantity_full: r.get_quantity(),
                    price: r.get_price_with_tax(),
                    product_id: r.get_product().id,
                };
            });

            // Send without repeating on failure
            return rpc
                .query({
                    model: "wechat.order",
                    method: "create_qr",
                    kwargs: {
                        lines: lines,
                        order_ref: order.uid,
                        pay_amount: order.get_due(),
                        terminal_ref: terminal_ref,
                        pos_id: pos_id,
                        journal_id: pm.wechat_journal_id[0],
                    },
                })
                .then(function (data) {
                    if (data.code_url) {
                        self.on_payment_qr(order, data.code_url);
                    } else if (data.error) {
                        self.show_warning(data.error);
                    } else {
                        self.show_warning("Unknown error");
                    }
                });
        },
    });

    const PosWeChatPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            addNewPaymentLine({detail: paymentMethod}) {
                if (paymentMethod.wechat_method === "native") {
                    this.env.pos.wechat_qr_payment(this.currentOrder, paymentMethod);
                    return true;
                }
                return super.addNewPaymentLine.apply(this, arguments);
            }
        };

    Registries.Component.extend(PaymentScreen, PosWeChatPaymentScreen);

    var PaymentlineSuper = models.Paymentline;
    models.Paymentline = models.Paymentline.extend({
        initialize: function (attributes, options) {
            PaymentlineSuper.prototype.initialize.apply(this, arguments);
            this.micropay_id = options.micropay_id;
        },
        // TODO: do we need to extend init_from_JSON too ?
        export_as_JSON: function () {
            var res = PaymentlineSuper.prototype.export_as_JSON.apply(this, arguments);
            res.micropay_id = this.micropay_id;
            return res;
        },
    });
});
