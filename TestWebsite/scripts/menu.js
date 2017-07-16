var active = 0;
	ids = {"st": "storm", "nb": "neville", "js": "jenny", "sc": "stephen"};

$(document).ready(function(){
	$("#nav_dropdown_container").click(function(){
		if(active){
			$("#nav_dropdown").css({"visibility": "hidden", "opacity": "0"});
			active = 0;
		}

		else{
			$("#nav_dropdown").css({"visibility": "visible", "opacity": "1"});
			active = 1;
		}
	})

	$(".nav_item").click(function(){
		var id = $(this).attr("id");
			new_id = "#" + ids[id];

		$('html, body').animate({ scrollTop: $(new_id).offset().top - 50});
	})
})
