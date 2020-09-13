function update_length() {
  $.getJSON( "/data", function( data ) {
    $("#length").html(data.length);
  });
}

window.setInterval(update_length, 5000);
update_length();

