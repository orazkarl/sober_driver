var status_check;
var lId;
var lIdD;
var co;
function get_application(send_url, name, lastId, lastIdDel, check_order) {
	if (!status_check) return;
	lId = lastId;
	lIdD = lastIdDel;
	co = check_order;
	$.ajax({
		url: send_url,
		type: 'POST',
		data: name+"=1&lastId="+lId+"&lastIdDel="+lastIdDel+"&check_order="+co,
		dataType: "json",
		success: function(res) {
			lId = res.lastId;
			lIdD = res.lastIdDel;
			if (res.check_order) {
				co = res.check_order;
			}
			if (res.js) {
				eval(res.js);
			}
			get_application(send_url, name, lId, lIdD, co);
		},
		error: function(e) {
			if (e.status == 500) {
				alert("Ошибка на стороне сервера. Пожалуйста, повторите попытку ещё раз.");
				return;
			} else {
				setTimeout(function() {
					get_application(send_url, name, lId, lIdD, co);
				}, 3000);
			}
		}
	});
}
function notification(msg, id) {
	let ids = localStorage.getItem("notification");
	ids = JSON.parse(ids);
	if (ids == null) ids = [];
	ids.push(id);
	ids = JSON.stringify(ids);
	localStorage.setItem("notification", ids);
	let idMsg = new Date().getTime();
	$("#notif").append("<div class='msg' id='notif_msg_"+idMsg+"'><span class='notif_close' data-id='"+idMsg+"'>&times;</span><div>"+msg+"</div></div>");
}
function editApp(id, number) {
	for (let i = 0; i < id.length; i++) {
		$("#button_cancel_"+id[i]).text("Нельзя отменить");
		$("#phone_"+id[i]).html("<a href='tel:"+number[i]+"'>"+number[i]+"</a>");
		$("#app_"+id[i]).css("background", "#c8ffc1");
	}
}
$(document).ready(function() {
	function parse_local() {
		let ids = localStorage.getItem("notification");
		if (ids == null) {
			$(".msg").remove();
		}
	}
	let path_url = window.location.pathname.split('/').pop();
	if (path_url == "orders") {
		setInterval(function() {
			parse_local();
		}, 500);
		let ids = localStorage.getItem("notification");
		ids = JSON.parse(ids);
		if (ids != null) {
			let idMsg = new Date().getTime();
			$("#notif").append("<div class='msg' id='notif_msg_"+idMsg+"'><span class='notif_close' data-id='"+idMsg+"'>&times;</span><div>У вас есть активные заказы ("+ ids.length +"шт.)<br><a href='/shipped' target='_blank'>Перейти</a></div></div>");
		}
	}
	$(".table_applications").on("click", ".send_app", function(e) {
		e.preventDefault();
		$(".bg_modal").fadeIn();
		$("#set_app #order_id").val($(this).data('id'));
	});
	$("#notif").on("click", ".notif_close", function() {
		let id = $(this).data("id");
		$("#notif_msg_"+id).remove();
	});
	$(".bg_modal #close").click(function() {
		$(".bg_modal").fadeOut();
	})
	$("#statisOrder_a").click(function() {
		$("#statisOrder").slideToggle();
	});
	$("#filterCity #city").change(function() {
		if ($(this).val() == "all") {
			location.href = path_url;
			return;
		}
		$("#filterCity").submit();
	});
	$("#paramSearch").change(function() {
		if ($(this).val() == "date") {
			$("#question").mask("99.99.9999 - 99.99.9999",{autoclear: false});
		} else {
			$("#question").unmask();	
		}
	});
	$("#formSearch").submit(function(e) {
		if ($("#paramSearch").val() == "no") {
			e.preventDefault();
			alert("Выберите параметр поиска");
			$("#paramSearch").focus();
		}
	});
	
	$('#filterCity option:contains("'+selectedFilterCity+'")').attr("selected", true);
	$('#formSearch option[value="'+selectedParam+'"]').attr("selected", true);
	if (selectedParam == "date") {
		$("#question").mask("99.99.9999 - 99.99.9999",{autoclear: false});
	} else {
		$("#question").unmask();	
	}
	
	$(".answer_a").click(function(e) {
		e.preventDefault();
		$(".bg_modal").fadeIn();
		$("#form_answer #qId").val($(this).data('id'));
	});

	$("#editCity").change(function() {
		let id = $(this).val();
		if (id == "no") {
			$("#edit_city #hiddenInputs").slideUp();
			return;
		}
		$("#edit_city #name").val(objectCity[id].city);
		$("#edit_city #price").val(objectCity[id].price);
		$("#edit_city #tariff").val(objectCity[id].tariff);
		$("#edit_city #period").val(objectCity[id].period);
		$("#edit_city #hiddenInputs").slideDown();
	});

	$("#sumBalance").keyup(function() {
		let sum = $(this).val() / 0.93;
		$(".hint").show().find("#commission").text(sum.toFixed(2));
	});

	$(".sidebar").click(function(e) {
		e.preventDefault();
		let menu = $(".menu");
		if (menu.css("display") == "none") {
			menu.css("display", "table");
			$(this).html("&times;").css("color", "#555");
		} else {
			menu.hide();
			$(this).html("&equiv;").css("color", "#fff");
		}
	});

	$("input[type='tel']").mask("+7 (999) 999-99-99",{autoclear: false});
	$('#number_yd').mask('aa № 999999',{autoclear: false});
});