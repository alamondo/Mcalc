$(document).ready(function() {
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  $("#day_button").addClass("activated");

  var add_button_state = false;

  $(".scope_button").on("click", function() {
    $(".scope_button")
      .not(this)
      .removeClass("activated");
    $(this).addClass("activated"); //eventually removeClass of some previous class
    // other stuff
  });

  function myMove() {
    var elem = document.getElementById("in_button");
    var pos = 0;
    var id = setInterval(frame, 10);
    function frame() {
      if (pos == 350) {
        clearInterval(id);
      } else {
        pos++;
        elem.style.top = pos + "px";
        elem.style.left = pos + "px";
      }
    }
  }

  $("#add_button").click(async function() {
    if (add_button_state == false) {
      $("#in_button").addClass("visible");
      move_horizontal("in_button", 40, 10, 280);
      $("#out_button").addClass("visible");
      move_vertical("out_button", 40, 10, 280);
      add_button_state = true;
    } else {
      move_vertical("out_button", 280, -10, 40);
      move_horizontal("in_button", 280, -10, 40);
      await sleep(100);
      $("#out_button").removeClass("visible");
      $("#in_button").removeClass("visible");
      add_button_state = false;
    }
  });

  function move_vertical(name, start_pos, delta, end_pos) {
    var elem = document.getElementById(name);
    var pos = start_pos;
    var id = setInterval(frame, 1);
    function frame() {
      if (pos == end_pos) {
        clearInterval(id);
      } else {
        pos += delta;
        elem.style.bottom = pos + "px";
      }
    }
  }

  function move_horizontal(name, start_pos, delta, end_pos) {
    var elem = document.getElementById(name);
    var pos = start_pos;
    var id = setInterval(frame, 1);
    function frame() {
      if (pos == end_pos) {
        clearInterval(id);
      } else {
        pos += delta;
        elem.style.right = pos + "px";
      }
    }
  }

  $("#nav a").click(function() {
    $("#ajax-content")
      .empty()
      .append(
        "<div class='loading'><img src='static/loading.svg' alt='Loading' /></div>"
      );
    $("#nav a").removeClass("current");
    $(this).addClass("current");

    $.ajax({
      url: this.href,
      success: function(html) {
        $("#ajax-content")
          .empty()
          .append(html);
      }
    });
    return false;
  });

  $("#ajax-content")
    .empty()
    .append(
      "<div class='loading'><img src='static/loading.svg' alt='Loading' /></div>"
    );
  $.ajax({
    url: "day",
    success: function(html) {
      $("#ajax-content")
        .empty()
        .append(html);
    }
  });
});
