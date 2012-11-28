/*  
==================================================================
        AJAX FORM FUNCTIONS
==================================================================
*/
function apply_form_field_error(fieldname, error) {
    var input = $("#" + fieldname),
        container = $("#" + fieldname + "-form"),
        error_msg = $("<span />").addClass("alert-error ajax-error").text(error[0]);

    container.addClass("error");
    error_msg.insertAfter(container);
}

function clear_form_field_errors(form) {
    $(".ajax-error", $(form)).remove();
    $(".error", $(form)).removeClass("error");
}

function ajaxFormShow() {
    $("#ajax-form").slideDown("medium");
}

function ajaxFormHide() {
    $("#ajax-form").fadeOut("medium");
}

function successFormHide() {
    $("#ajax-success").fadeOut("medium");
}

function showSuccess() {
    ajaxFormHide();
    $("#ajax-success").delay(800).slideDown("medium").delay(1800).fadeOut("medium");
}

function getCookie(name) {
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
        success: function(data, textStatus, jqXHR) {
            // window.location.reload();
            showSuccess();
        },
        error: function(data, textStatus, jqXHR) {
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
$(document).ready(function() {
    $('.btn-share').popover({
        html: true
    });
});


/*  
==================================================================
        INITIATE FITVIDS
==================================================================
*/
// $(document).ready(function(){
//     $("#damon-video").fitVids();
// });


/*  
==================================================================
        SANITATION MAP FUNCTIONS
==================================================================
*/
$(document).ready(function(){

    var sanitation_number = 58;

    $('#world').mapster({
        render_highlight: {
            fillOpacity: 0.2,
            stroke: false,
            altImage: staticURL + 'image/sanitation-map-white.png'
        },
        render_select: {
            fillOpacity: 1.0,
            stroke: false,
            altImage: staticURL + 'image/sanitation-map-red.png'
        },
        fadeInterval: 50,
        mapKey: 'region',
  listSelectedClass: 'selected',
        areas: [
        {
            key: 'af',
            selected: true,
                isSelectable: true
        }],
        onClick: function (data) {
    var regions_total = $('#map-regions'),
            sanitation_total = $('#map-number'),
                    stats = {
                        af: ['Africa', 'af', 58],
                        la: ['Latin America + Caribbean', 'la', 12],
                        ae: ['Anglo-America + Europe', 'ae', 2],
                        wa: ['South/West Asia + Commonwealth', 'sa', 113],
                        ea: ['East/Southeast Asia + Oceania', 'ea', 81] 
                    }
            if ( data.selected == true ) {
                regions_total.append('<li class="' + stats[data.key][1] + '">' + stats[data.key][0] + '</li>' );
                sanitation_number += stats[data.key][2];
                    // console.log(sanitation_number);
            } else {
                regions_total.children('li.' + stats[data.key][1]).remove();
                sanitation_number -= stats[data.key][2];
                    // console.log(sanitation_number);
            }
            sanitation_total.animate({
                opacity: 0,
              }, 500, function() {
                sanitation_total.text((sanitation_number/100)).animate({
                    opacity: 1,
                }, 500);
              });
            return sanitation_number;
    }
    });
});


/*  
==================================================================
        FLIP RIBBON FUNCTIONS
==================================================================
*/
$(function () {
    if ($('html').hasClass('csstransforms3d')) {
        $('.card').removeClass('scroll').addClass('flip');
        $('.card.flip').hover(
            function () {
                $(this).find('.card-wrapper').addClass('flipIt');
            },
            function () {
                $(this).find('.card-wrapper').removeClass('flipIt');           
            }
        );
    } else {
        $('.card').hover(
            function () {
                $(this).find('.card-detail').stop().animate({bottom:0}, 500, 'easeOutCubic');
            },
            function () {
                $(this).find('.card-detail').stop().animate({bottom: ($(this).height() * -1) }, 500, 'easeOutCubic');          
            }
        );
    }
});


/*  
==================================================================
        TRACKING/SHARING FUNCTIONS
==================================================================
*/
function trackMapFacebook() {
    _gaq.push(['_trackEvent', 'Sanitation Map', 'Share', 'Facebook']);
}
function trackMapTwitter() {
    _gaq.push(['_trackEvent', 'Sanitation Map', 'Share', 'Twitter']);
}
function trackMapPinterest() {
    _gaq.push(['_trackEvent', 'Sanitation Map', 'Share', 'Pinterest']);
}
function trackMapGooglePlus() {
    _gaq.push(['_trackEvent', 'Sanitation Map', 'Share', 'GooglePlus']);
}
function trackMapLinkedIn() {
    _gaq.push(['_trackEvent', 'Sanitation Map', 'Share', 'LinkedIn']);
}


function trackStoryFacebook() {
    _gaq.push(['_trackEvent', 'Story', 'Share','Facebook', socialPostTitle ]);
}
function trackStoryTwitter() {
    _gaq.push(['_trackEvent','Story', 'Share','Twitter', socialPostTitle ]);
}
function trackStoryPinterest() {
    _gaq.push(['_trackEvent', 'Story', 'Share','Pinterest', socialPostTitle ]);
}
function trackStoryGooglePlus() {
    _gaq.push(['_trackEvent', 'Story', 'Share','GooglePlus', socialPostTitle ]);
}
function trackStoryLinkedIn() {
    _gaq.push(['_trackEvent', 'Story', 'Share','LinkedIn', socialPostTitle ]);
}


function shareMapFacebook() {
    window.open('http://www.facebook.com/share.php?u=' + socialMapLink + '&title=' + socialMapTitleEscaped,'Share on Facebook','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}
function shareMapTwitter() {
    window.open('http://twitter.com/home?status=' + socialMapTitleEscaped + '+' + socialMapLink,'Share on Twitter','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}
function shareMapPinterest() {
    window.open('http://pinterest.com/pin/create/button/?url=' + socialMapLink + '&media=' + socialMapImage + '&description=' + socialMapTitleEscaped,'Share on Pinterest','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}
function shareMapGooglePlus() {
    window.open('https://plus.google.com/share?url=' + socialMapLink,'Share on Google Plus','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}
function shareMapLinkedIn() {
    window.open('http://www.linkedin.com/shareArticle?mini=true&url=' + socialMapLink + '&title=' + socialMapTitleEscaped + '&source=' + socialMapLink,'Share on LinkedIn','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}


function shareStoryFacebook() {
    window.open('http://www.facebook.com/share.php?u=' + socialPostLink + '&title=' + socialPostTitleEscaped,'Share on Facebook','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
    console.log('shared');
}
function shareStoryTwitter() {
    window.open('http://twitter.com/home?status=' + socialPostTitleEscaped + '+' + socialPostLink,'Share on Twitter','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}
function shareStoryPinterest() {
    window.open('http://pinterest.com/pin/create/button/?url=' + socialPostLink + '&media=' + socialPostImage + '&description=' + socialPostTitleEscaped,'Share on Pinterest','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}
function shareStoryGooglePlus() {
    window.open('https://plus.google.com/share?url=' + socialPostLink,'Share on Google Plus','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}
function shareStoryLinkedIn() {
    window.open('http://www.linkedin.com/shareArticle?mini=true&url=' + socialPostLink + '&title=' + socialPostTitleEscaped + '&source=' + socialPostLink,'Share on LinkedIn','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
}