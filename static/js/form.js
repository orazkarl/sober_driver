$(document).ready(function() {
	$("body").on("submit", "form[name]", function (e) {
		e.preventDefault();
		let button = $('button[type="submit"]', $(this));
		button.attr("disabled", true);

		let data = new FormData($(this).get(0));
		data.append($(this).attr('name'), "1");
		
		$.ajax({
			type: $(this).attr("method"),
			dataType: 'json',
			url: $(this).attr("action"),
			data: data,
			contentType: false,
			processData: false,
			success: function(res){
				if (res.msg) {
					alert(res.msg);
				} else if (res.go) {
					location.href = res.go;
				} else if (res.js) {
					eval(res.js);
				} else {
					alert("Неизвестная ошибка!");
				}
				button.attr("disabled", false);
			},
			error: function() {
				alert("Ошибка на сервере. Пожалуйста, повторите попытку позже.");
				button.attr("disabled", false);
			}
		});
	});
	$(document).on("click", ".send", function (e) {
		if (name = $(this).data("name")) {
			e.preventDefault();
			if (val = $(this).data("send-val")) {
				$('form[name='+name+'] input').val(val);
			}
			if (text = $(this).data("confirm")) {
				if (!confirm(text)) return false;
			}
			$('form[name='+name+']').submit();
		}
	});
});