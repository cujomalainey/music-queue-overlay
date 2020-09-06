var remove_offset = 0;

function update_queue() {
  $.getJSON( "/data", function( data ) {
    data['queue'].forEach(insert_queue);
    trim_queue(data['queue']);
    remove_offset = 0;
  });
}

function trim_queue(data) {
  l = $("#queue").children("li");
  for (i = data.length + remove_offset; i <= l.length; i++) {
    remove_element(l[i]);
  }
}

function build_elements(data) {
  li = document.createElement("li");
  d = document.createElement("div");
  h1 = document.createElement("h1");
  h3 = document.createElement("h3");
  img = document.createElement("img");
  $(li).append(d);
  $(d).append(img);
  $(d).append(h1);
  $(d).append(h3);
  $(img).attr("src", data['thumbnails']['default']['url']);
  $(img).addClass("thumbnail");
  $(h1).html(data['title']);
  $(h3).html(data['channelTitle']);
  $(li).hide();
  return li;
}

function remove_element(node) {
  $(node).slideUp(400, function() {
    $(node).remove();
  });
}

function insert_queue(value, index, array) {
  l = $("#queue").children("li");
  found = false;
  var remove_count = 0;
  for (i = index; i + remove_offset < l.length; i++) {
    var offset = remove_offset + i;
    if ($(l[offset]).find('h1').html() == value['title']) {
      found = true;
      break;
    } else {
      remove_element(l[offset]);
      remove_count += 1;
    }
  }
  if (!found) {
    new_node = build_elements(value);
    $("#queue").append(new_node);
    $(new_node).slideDown();
  }
  if (index == 0) {
    $(l[offset]).find("div").addClass("rainbow");
  } else {
    $(l[offset]).find("div").removeClass("rainbow");
  }
  remove_offset += remove_count;
}

window.setInterval(update_queue, 5000);
update_queue();

