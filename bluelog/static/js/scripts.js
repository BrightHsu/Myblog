$(function(){
    function render_time() {
        return moment($(this).data('timestamp')).format('lll')
    }
    $('[data-toggle=tooltip]').tooltip(
        {title: render_time}
    )
})

$(function(){
  var typed = new Typed('#typed', {
    stringsElement: '#typed-strings',
    typeSpeed: 50, //打字速度
    backSpeed: 20, //回退速度
    showCursor: true, // 显示光标
    cursorChar: '!', //光标元素
  });

})