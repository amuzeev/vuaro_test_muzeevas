$(document).ready(function(){

    //Пометка на удаление
    var remove_picture_btn_css = '.img-thumbnail .picture-remove';
    var delete_check_css = '.delete-check input';

    $(document).on( "click", remove_picture_btn_css, function() {
        var btn = $(this);
        var delete_check = btn.parent().find(delete_check_css);

        if (delete_check.is(':checked')){
            btn.removeClass('btn-danger').addClass('btn-default');
            delete_check.prop('checked', false);
        }
        else{
            btn.removeClass('btn-default').addClass('btn-danger');
            delete_check.prop('checked', true);
        }
    });


    //Отправка на почту
    var send_email_css = '#send_email';
    $(document).on( "click", send_email_css, function() {
        var btn = $(this);
        btn.attr('disabled','disabled');

        $.ajax({
            url: '/send_pictures/',
            success: function(data, textStatus, jqXHR ){
                $('.email_block .alert-success').removeClass('hidden');
            },
            error: function(jqXHR, textStatus, errorThrown){
                $('.email_block .alert-danger').removeClass('hidden');
            },
            complete: function(jqXHR, textStatus){
                btn.removeAttr('disabled')
            }
        });

    });
});



