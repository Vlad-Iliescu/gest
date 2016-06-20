$(document).ready(function() {
    $('.see_more').click(function() {
        var e = $(this);
        e.parent().find('.more').slideToggle(0);
        if (e.text() == '[more]') {
            e.html('[less]');
        } else {
            e.html('[more]');
        }
    });
    $('#show_all').click(function() {
       $('.more').each(function(index, item) {
            var e=$(this)
            e.slideToggle(0);
       });
       $('.see_more').each(function(index, item) {
            var e = $(this);
            if (e.text() == '[more]') {
                e.html('[less]');
            } else {
                e.html('[more]');
            }
       });
    });

	 $('#date, #date_useri').datepicker({
		altFormat: 'yy-mm-dd',
		dateFormat: 'yy-mm-dd',
		showOn: 'button',
		buttonImage: '/welcome/static/images/calendar.png',
		buttonImageOnly: true,
		maxDate: new Date()
	});

	$('#date').change(function() {
		$('#curent_date').html($(this).val());
		$.post('/rapoarte/facturi_luna',{data : $(this).val()},
			function(data) {
				$('#for_table').html(data);
			}
		);
	});
	
	$('#date_useri').change(function() {
		$('#curent_date').html($(this).val());
		$.post('/rapoarte/useri_luna',{data : $(this).val()},
			function(data) {
				$('#for_table').html(data);
			}
		);
	});


	$('#date, #date_useri').change();

});