function update_queue() {
  $.getJSON( "ajax/test.json", function( data ) {
    console.log(data);
  });
}

window.setInterval(update_queue, 10000);
