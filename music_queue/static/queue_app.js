function update_queue() {
  $.getJSON( "/data", function( data ) {
    console.log(data);
  });
}

window.setInterval(update_queue, 10000);
