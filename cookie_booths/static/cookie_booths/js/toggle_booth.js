$(document).ready(function () {
  $("#booth_blocks").DataTable({
    paging: false,
  });
});

function toggleBooth(booth_id, action) {
  $.ajax({
    url: location.origin + "/booths/blocks/enable_booth_days/" + action,
    type: "POST",
    data: {
      booth_id: booth_id,
    },
    success: function () {
      window.location.reload();
    },
  });
}

function EnableBooth(booth_id) {
  toggleBooth(booth_id, "enable");
}

function DisableBooth(booth_id) {
  toggleBooth(booth_id, "disable");
}
