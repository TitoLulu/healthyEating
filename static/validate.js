
$(function() {
    $('button').click(function() {
        var email = $('#email').val();
        var pwd = $('#pwd').val();
        $.ajax({
            url: '/login',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);

            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});
