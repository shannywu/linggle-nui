$('.more').click(function() {
    // expand($('div.text0'))
    var content = $(this).parent().children('.text');
    var contentHeight = content.data('contentHeight');

    if(!!!contentHeight){
        contentHeight = determineActualHeight(content);
        content.data('contentHeight', contentHeight);
    }
    content.stop().animate({ 
        height: (contentHeight == content.height() ? 165 : contentHeight)
    }, 300);

    var button = $(this).children('span');
    if (button.hasClass('glyphicon-chevron-down')) {
        button.removeClass('glyphicon-chevron-down').addClass("glyphicon-chevron-up");
    }
    else {
        button.removeClass("glyphicon-chevron-up").addClass("glyphicon-chevron-down");
    }
})

$('.merge-heading').click(function() {
    // expand($('div.text0'))
    var content = $(this).attr('data-target');
    var handler = $(this);

    $('.merge-block').each(function(index){
        if(content == $(this).attr('data')){
            // $(this).attr('data');
            var contentHeight = $(this).data('contentHeight');

            if(!!!contentHeight){
                contentHeight = determineActualHeight($(this));
                $(this).data('contentHeight', contentHeight);
            }
            $(this).stop().animate({ 
                height:  (contentHeight == $(this).height() ? 0 : contentHeight)
            },
            
            {duration: 1000,complete: function(){
                var button = handler.children('span');
                if (button.hasClass('glyphicon-plus')) {
                    button.removeClass('glyphicon-plus').addClass("glyphicon-minus");
                }
                else {
                    button.removeClass("glyphicon-minus").addClass("glyphicon-plus");
                }
            }}
            );
      }
    });
})

function determineActualHeight(div) {
    var clone = div.clone().hide().css('height', 'auto').appendTo(div.parent()),
    height = clone.height();
    clone.remove();
    return height;
}

