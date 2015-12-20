$('#more0').click(function() {
    expand($('div.text0'))
})
$('#more1').click(function() {
    expand($('div.text1'))
})
$('#more2').click(function() {
    expand($('div.text2'))
})
$('#more3').click(function() {
    expand($('div.text3'))
})

function expand($div){
    var contentHeight = $div.data('contentHeight');
 
    if(!!!contentHeight){
        contentHeight = determineActualHeight($div);
        $div.data('contentHeight', contentHeight);
    }
    $div.stop().animate({ 
        height: (contentHeight == $div.height() ? 120 : contentHeight)
    }, 1000);
}
 
function determineActualHeight($div) {
    var $clone = $div.clone().hide().css('height', 'auto').appendTo($div.parent()),
    height = $clone.height();
    $clone.remove();
    return height;
}

