jQuery(function(){
    var img = document.getElementById('target');
    var width = img.naturalWidth;
    var height = img.naturalHeight;

    jQuery('#target').Jcrop({
        trueSize: [width,height],
        onSelect: updateCoords
    });

});

function updateCoords(c) {
    jQuery('#x1').val(c.x);
    jQuery('#y1').val(c.y);
    jQuery('#x2').val(c.x2);
    jQuery('#y2').val(c.y2);
    jQuery('#w').val(c.w);
    jQuery('#h').val(c.h);
};

function checkCoords() {
    if (parseInt(jQuery('#w').val())>0) {
        return true;
    }
    event.preventDefault();
    $("#alert").show();
    return false;

};

