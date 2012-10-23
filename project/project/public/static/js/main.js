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

// Ajax Form animation
function ajaxFormShow() {
	$("#ajax-form").slideDown("medium");
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