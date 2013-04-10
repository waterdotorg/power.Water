/*  
==================================================================
        AJAX FORM FUNCTIONS
==================================================================
*/
function apply_form_field_error (fieldname, error) {
    var input = $("#" + fieldname),
        container = $("#" + fieldname + "-form"),
        error_msg = $("<span />").addClass("alert-error ajax-error").text(error[0]);

    container.addClass("error");
    error_msg.insertAfter(container);
}

function clear_form_field_errors (form) {
    $(".ajax-error", $(form)).remove();
    $(".error", $(form)).removeClass("error");
}

function ajaxFormShow() {
    $("#ajax-form").slideDown("medium");
}

function ajaxFormHide() {
    $("#ajax-form").slideUp("medium");
}

function successFormHide() {
    $("#ajax-success").fadeOut("medium");
}

function showSuccess() {
    ajaxFormHide();
    $("#ajax-success").delay(800).fadeIn("medium").delay(1800).fadeOut("medium");
}

function hideMobileNav() {
    $(".mobile-nav-btn").fadeOut("medium");
}

function showMobileNav() {
    $(".mobile-nav-btn").fadeIn("medium");
}

function getCookie (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');


/*  
==================================================================
        SUBMIT AND SEND SETTINGS FORM
==================================================================
*/
$(document).on("submit", "#settings-form", function(e) {
    clear_form_field_errors($("#settings-form"));
    e.preventDefault();
    var self = $(this);
    var form_data = {
            first_name: self.find("#id_first_name").val(),
            last_name: self.find("#id_last_name").val(),
            email: self.find("#id_email").val(),
            csrfmiddlewaretoken: self.find("input[name='csrfmiddlewaretoken']").val()
        }
    if (self.find("#id_enable_email_updates").is(':checked')) {
        form_data.enable_email_updates = true;
    }
    if (self.find("#id_enable_facebook_updates").is(':checked')) {
        form_data.enable_facebook_updates = true;
    }
    if (self.find("#id_enable_twitter_updates").is(':checked')) {
        form_data.enable_twitter_updates = true;
    }

    var url = self.attr("action");
    ajax_req = $.ajax({
        url: url,
        type: "POST",
        data: form_data,
        success: function (data, textStatus, jqXHR) {
            $("#user-settings").delay(100).slideUp();
            var $settings = $("#user-settings");
            var $button = $(".mobile-nav-btn");
            if ($settings.hasClass("settings-open")) {
                $settings.removeClass("settings-open");
                $button.removeClass("button-hidden");
            } else {
                $settings.addClass("settings-open");
                $button.addClass("button-hidden");
            }
            showSuccess();
        },
        error: function (data, textStatus, jqXHR) {
            var errors = $.parseJSON(data.responseText);
            $.each(errors, function(index, value) {
                if (index === "__all__") {
                    django_message(value[0], "error");
                } else {
                    apply_form_field_error(index, value);
                }
            });
        }
    });
});


/*  
==================================================================
        BOOTSTRAP FUNCTIONS
==================================================================
*/  

$(document).ready(function () {

    // Changes Posts on Click
    // $('.post:gt(0)').hide();
    // $('.previous').click(function (e) {
    //     e.preventDefault();
    //     $('.post:first-child').fadeOut();
    //     $('.post:last-child').prependTo('#posts').fadeIn();
    // });
    // $('.next').click(function (e) {
    //     e.preventDefault();
    //     $('.post:first-child').fadeOut().next('.post').fadeIn().end().appendTo('#posts');
    // });

    // set panels equal to window size
    setPanelSize();
    setBackgroundImage();

    $(window).resize(function () {
        setPanelSize();
        setBackgroundImage();
    });

     // function to set panels to window size and constrain video
    function setPanelSize () {
        var windowHeight = $(window).height(),
            windowWidth = $(window).width(),
            $areaFull = $('.area-full'),
            $heroText = $('.hero-text'),
            $postNav = $('.post-navigation a');
        
        if (windowWidth > 767) {
            $areaFull.css({'height':(windowHeight-110)+'px'});
            $heroText.css({'top':(windowHeight*0.45)+'px'});
            if (windowHeight > 590) {
                $postNav.css({'height': (windowHeight-110)+'px'});
            }
            if (windowHeight < 320) {
                $heroText.css({'top':'200px'});
            }
        } else if (windowWidth > 480) {
            $heroText.css({'top':(windowHeight*0.45)+'px'});
            if (windowHeight > 590) {
                $areaFull.css({'height':'580px'});
                $postNav.css({'height':'580px'});
            }
            if (windowHeight < 320) {
                $heroText.css({'top':'200px'});
            }
        } else {
            $heroText.css({'top':'200px'});
            $areaFull.css({'height':'480px'});
            if (windowHeight > 590) {
                $areaFull.css({'height':'580px'});
                $postNav.css({'height':'580px'});
            }
            if (windowHeight < 320) {
                $heroText.css({'top':'200px'});
            }
        }
    }

    function setBackgroundImage () {
        $('.area-full').each(function () {
            var windowWidth = $(window).width();

            if (windowWidth > 480) {
                $(this).css('background-image', desktopImg);
            } else {
                $(this).css('background-image', mobileImg);
            }
        });
    }


    // Toggles settings form
    $(".settings-icon").click(function (e) {
        e.preventDefault();
        var $settings = $("#user-settings");
        var $button = $(".mobile-nav-btn");
        $settings.slideToggle("medium");
        if ($settings.hasClass("settings-open")) {
            $settings.removeClass("settings-open");
            $button.removeClass("button-hidden");
        } else {
            $settings.addClass("settings-open");
            $button.addClass("button-hidden");
        }
    });

    // Toggles settings form
    $("#user-settings .close").click(function (e) {
        e.preventDefault();
        $("#user-settings").slideUp("medium");
        var $settings = $("#user-settings");
        var $button = $(".mobile-nav-btn");
        if ($settings.hasClass("settings-open")) {
            $settings.removeClass("settings-open");
            $button.removeClass("button-hidden");
        } else {
            $settings.addClass("settings-open");
            $button.addClass("button-hidden");
        }
    });

    // Close Email Form
    $('#ajax-form .close').click(function (e) {
        e.preventDefault();
        $("#ajax-form").fadeOut("medium");
    })

    // Open links in a New Window
    $('.external').click(function () {
      $(this).attr('target', '_blank');
    });

    // Share Button
    $('.share-video').click(function () {
        $('.social-btns').fadeToggle('medium');
    });

    // Nav Orientation
    var path = window.location.href;
    $('.nav a').each(function () {
        if (this.href === path) {
            $(this).find('.nav-icon').addClass('nav-active');
        }
    });

    // Nav Labels
    $('.nav li').hover(function () {
        $(this).find('span.label').fadeToggle('fast');
    });

    // Toggles settings form
    $(".story-toggle").click(function () {
        // $("#featured-post").slideToggle("medium");
        // $(this).toggleClass("open");
        // if ($(this).hasClass("open")) {
        //     $(this).text('CLOSE STORY').append('<span> - </span>');
        // } else {
        //     $(this).text('MORE ABOUT THIS PHOTO').append('<span> + </span>');
        // }
        $('html, body').animate({scrollTop: $("#featured-post").offset().top-60}, 500);
    });


    $('.mobile-nav-btn').click(function (e){
        e.preventDefault();
        if ($(this).hasClass('.mobile-nav-btn-nav-visible')) {
            $('.mobile-nav').removeClass('mobile-nav-visible');
            $('.wrap').removeClass('wrap-nav-open');
            $(this).removeClass('.mobile-nav-btn-nav-visible');
            $('.mobile-settings-btn').removeClass('mobile-settings-btn-hidden');
            
        } else {
            $('.mobile-nav').addClass('mobile-nav-visible');
            $('.wrap').addClass('wrap-nav-open');
            $(this).addClass('.mobile-nav-btn-nav-visible');
            $('.mobile-settings-btn').addClass('mobile-settings-btn-hidden');
        }
    });

    $('.close-mobile-nav').click(function (e){
        e.preventDefault();
        $('.mobile-nav').removeClass("mobile-nav-visible");
        $('.wrap').removeClass('wrap-nav-open');
        $('.mobile-nav-btn').removeClass('.mobile-nav-btn-nav-visible');
        $('.mobile-settings-btn').removeClass('mobile-settings-btn-hidden');
    });

});



/*  
==================================================================
        TRACKING/SHARING FUNCTIONS
==================================================================
*/
// Variables defined in base.html

$(document).ready(function() {
    // Sign In Tracking
    $('#signInFacebook').click(function () {
        _gaq.push(['_trackEvent', '2_signin_page', 'button_facebook']);
    });

    $('#signInTwitter').click(function () {
        _gaq.push(['_trackEvent', '2_signin_page', 'button_twitter']);
    });
    
    // Other Tracking Functions
    $('#trackSupportEvent').click(function () {
        _gaq.push(['_trackEvent', '1_landing_page', 'button_right_signin', userPK ]);
    });

    $('#trackSupportEventLarge').click(function () {
        _gaq.push(['_trackEvent', '1_landing_page', 'button_bottom_signin', userPK ]);
    });

    $('#trackDonateEvent').click(function () {
        _gaq.push(['_trackEvent', '1_landing_page', 'button_right_donate', userPK ]);
    });

    $('#trackSubscribeEvent').click(function () {
        _gaq.push(['_trackEvent', '1_landing_page', 'button_right_subscribe', userPK ]);
    });

    $('#trackInstagramEvent').click(function () {
        _gaq.push(['_trackEvent', '3_dashboard_page', 'button_instagram_click', userPK ]);
    });

    // Sharing Buttons with Tracking Functions
    // $('#shareFacebook').click(function (e) {
    //     window.open('http://www.facebook.com/share.php?u=' + shareLink + '&title=' + shareTitle,'Facebook','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
    //     _gaq.push(['_trackEvent', '1_home_page', 'button_facebook_share', userPK ]);
    //     e.preventDefault();
    // });

    // $('#shareTwitter').click(function (e) {
    //     window.open('http://twitter.com/home?status=' + shareTitle + '+' + shareLink,'Twitter','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
    //     _gaq.push(['_trackEvent', '1_home_page', 'button_twitter_share', userPK ]);
    //     e.preventDefault();
    // });

    // $('#sharePinterest').click(function (e) {
    //     window.open('http://pinterest.com/pin/create/button/?url=' + shareLink + '&media=' + shareImage + '&description=' + shareTitle,'Pinterest','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
    //     _gaq.push(['_trackEvent', '1_home_page', 'button_pinterest_share', userPK ]);
    //     e.preventDefault();
    // });

    // $('#shareGooglePlus').click(function (e) {
    //     window.open('https://plus.google.com/share?url=' + shareLink,'GooglePlus','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
    //     _gaq.push(['_trackEvent', '1_home_page', 'button_google_plus_share', userPK ]);
    //     e.preventDefault();
    // });

    // $('#shareLinkedIn').click(function (e) {
    //     window.open('http://www.linkedin.com/shareArticle?mini=true&url=' + shareLink + '&title=' + shareTitle + '&source=' + shareLink,'LinkedIn','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
    //     _gaq.push(['_trackEvent', '1_home_page', 'button_linked_in_share', userPK ]);
    //     e.preventDefault();
    // });

    // Dashboard Tracking Functions
    $('#trackFacebookInviteEvent').click(function (e) {
        window.open('https://www.facebook.com/dialog/feed?app_id=195104123845921&' + shareLink + '&picture=http://power.water.org/static/image/dashboard_well.jpg&name=Will%20You%20Join%20Us?&caption=Water.org%20and%20the%20water%20crisis&description=Donating%20your%20voice%20to%20the%20cause%20is%20easy%20and%20can%20make%20a%20difference.&redirect_uri=http://power.water.org/dashboard/','Facebook','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
        _gaq.push(['_trackEvent', '3_dashboard_page', 'button_facebook_invite', userPK ]);
        e.preventDefault();
    });

    $('.trackPhotoScrollEvent').click(function (e) {
        _gaq.push(['_trackEvent', '3_dashboard_page', 'button_share_photo', userPK ]);
        $('html, body').delay(300).animate({scrollTop: $(".blue-stripe").offset().top-200}, 500);
        e.preventDefault();
    });

    $('#trackPhotoScrollEvent').click(function (e) {
        _gaq.push(['_trackEvent', '1_landing_page', 'button_share_photo', userPK ]);
        $('html, body').delay(300).animate({scrollTop: $(".blue-stripe").offset().top-200}, 500);
        e.preventDefault();
    });

    $('#trackDonateEvent').click(function () {
        _gaq.push(['_trackEvent', '1_landing_page', 'button_donate', userPK ]);
    });

    $('#trackJoinEvent').click(function () {
        _gaq.push(['_trackEvent', '1_landing_page', 'button_join', userPK ]);
    });

    $('#trackLearnEvent').click(function () {
        _gaq.push(['_trackEvent', '3_dashboard_page', 'button_share_photo', userPK ]);
    });

    $('#trackTwitterInvite').click(function (e) {
        window.open('http://twitter.com/home?status=' + tweetTitle + '+' + shareLink,'Twitter','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
        _gaq.push(['_trackEvent', '3_dashboard_page', 'button_twitter_invite', userPK ]);
        e.preventDefault();
    });
});