$(document).ready(function() {

    $("#day_button").addClass('activated');

    $('.scope_button').on('click', function(){
        $('.scope_button').not(this).removeClass('activated');
        $(this).addClass('activated'); //eventually removeClass of some previous class
        // other stuff
    });

    $("#nav a").click(function() {

        $("#ajax-content").empty().append("<div id='loading'><img src='images/loading.gif' alt='Loading' /></div>");
        $("#nav a").removeClass('current');
        $(this).addClass('current');

        $.ajax({ url: this.href, success: function(html) {
            $("#ajax-content").empty().append(html);
            }
    });
    return false;
    });

    $("#ajax-content").empty().append("<div id='loading'><img src='images/loading.gif' alt='Loading' /></div>");
    $.ajax({ url: 'day', success: function(html) {
            $("#ajax-content").empty().append(html);
    }
    });
});
