$('.more').click(function() {
    // expand($('div.text0'))
    var content = $(this).parent().children('.text');
    var contentHeight = content.data('contentHeight');

    if(!!!contentHeight){
        contentHeight = determineActualHeight(content);
        content.data('contentHeight', contentHeight);
    }
    content.stop().animate({ 
        height: (contentHeight == content.height() ? 130 : contentHeight)
    }, 1000);

    var button = $(this).children('span');
    if (button.hasClass('glyphicon-chevron-down')) {
        button.removeClass('glyphicon-chevron-down').addClass("glyphicon-chevron-up");
    }
    else {
        button.removeClass("glyphicon-chevron-up").addClass("glyphicon-chevron-down");
    }
})

function determineActualHeight(div) {
    var clone = div.clone().hide().css('height', 'auto').appendTo(div.parent()),
    height = clone.height();
    clone.remove();
    return height;
}

