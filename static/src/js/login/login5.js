odoo.define('login4', function (require) {
    "use strict";

    var Login = function () {
        var handleLogin = function() {
            //数据库切换
            var currentdb = $("#db_list li.selected").text().trim();
            $(document).ready(function() {

                $("ul#db_list").on("click","li",function(){
                    $("#db").val($(this).text().trim());
                    if($(this).text().trim()!= currentdb)
                        window.location.href= '/web?db='+$(this).text().trim();

                })
            });

            $('.login-form input').keypress(function (e) {
                if (e.which == 13) {
                    if ($('.login-form').validate().form()) {
                        $('.login-form').submit();
                    }
                    return false;
                }
            });
        }
        return {
            init: function () {
                handleLogin();

                $('.login-bg').backstretch([
                        "/rainbow_community_theme/static/src/img/bg/bg1.jpg",
                        "/rainbow_community_theme/static/src/img/bg/bg2.jpg",
                        "/rainbow_community_theme/static/src/img/bg/bg3.jpg",
                        "/rainbow_community_theme/static/src/img/bg/bg4.jpg"
                    ], {
                        fade: 1000,
                        duration: 8000
                    }
                );
            }
        };
    }();

    jQuery(document).ready(function() {
        Login.init();
    });

});