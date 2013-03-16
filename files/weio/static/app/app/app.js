/**
 * SockJS
 * ------
 */

/**
 * Create SockJS object
 */
/** We are using tornado.web.StaticFileHandler */
var sockjs_url = '/app';

/** We are NOT using static file handler */
//var sockjs_url = 'http://localhost:8080/static/weio';	 

var sockjs = new SockJS(sockjs_url);

/**
 * ONOPEN
 */
sockjs.onopen = function() {
    // open
};

/**
 * ONMESSAGE
 */
sockjs.onmessage = function(e) {
    console.log(e.data); 

    var pydat = JSON.parse(e.data);

    // Present output
    $('#hello').append(" in " + pydat['load'] + " mode");

    $("#app-body").show();
};

/**
 * ONCLOSE
 */
sockjs.onclose   = function() {
    // close
};


/**
 * jQuery
 * ------
 */

$(document).ready(function(){
    $("#btn1").click(function(){
	    console.log('[C] Redirescting to Configurator');
        document.location.href='../wificon/wificon.html';
    });
});
