/**
 * SockJS
 * ------
 */

/**
 * Create SockJS object
 */
/** We are using tornado.web.StaticFileHandler */
var sockjs_url = '/weio';

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

function on_wifi_scan_rsp(rsp) {
    console.log("HERE 3");
    $('#scan-spin').hide();

    // Enable buttons
    $("#btn-app").removeAttr("disabled");
    $("#btn-ap").removeAttr("disabled");

    // Present output
    //$('#cfgrsp').html(e.data);

    // Nasty HACK : Jasnu rowlink bug https://github.com/twitter/bootstrap/issues/6302
    $('#cntb table').remove(); // Remove <table> leftovers : contents + class, not to confuse Jasny rowlink
    $('#cntb').append('<table class=\"table table-striped\" data-provides=\"rowlink\">' +
        '<thead><tr> <th>#</th> <th>ESSID</th> <th>Signal</th> <th>Encryption</th> </tr> </thead> <tbody>');

    for (var key in rsp) {
        console.log(rsp[key]);
    
        $('#cntb tbody').append('<tr><td>' + key + '</td>' +
            '<td>' + rsp[key].ESSID + '</td>' +
            '<td>' + rsp[key].Quality + '</td>' +
            '<td>' + rsp[key].Encryption + '</td>' +
            '<td><a href=\"javascript:App.Conn(\'' + rsp[key].ESSID + '\', \'' + rsp[key].Encryption +
                                    '\')\"><i class=\"icon-signin\"></i> Connect</a></td></tr>');
    }
    $('#cntb tbody').append('</tbody> </table>');


    $('#cntb table').rowlink(); // Jasny rowlink constructor. Has to be executed on the <table>, as #cntb seem to keep the class
}

function on_wifi_con_rsp(rsp) {
    console.log("HERE 4");
    $('#myModal').modal('hide');

    $("#modcon").removeAttr("disabled");
    $("#modal-passwd").show();
    $("#con-spinner").hide();
}

sockjs.onmessage = function(e) {
    //console.log(e.data);

    console.log("HERE 1");

    var pydat = JSON.parse(e.data);
    console.log(pydat['type'])

    switch (pydat['type'])
    {
        case "WIFI_SCAN_RSP" :
            console.log("HERE 2");
            on_wifi_scan_rsp(pydat['load']);
            break;

        case "WIFI_CON_RSP" :
            //on_wifi_con_rsp(pydat['load']);
            break;

        default :
            break;
    }
            
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

    $("#btn-app").click(function(){
	    console.log('[C] Going back to App');
        document.location.href='../app/app.html';
    });


    $("#btn-ap").click(function(){
	    console.log('[C] Goto AP Mode');
        $('#gone-modal').modal('show');
        App.Do(null, null)
    });
});

window.App = {};

App.Do = function(essid, passwd){
    var doconn = {};

    if (essid == null) {
        // AP Mode
        doconn.req_type="WEIO_AP_REQ"
    } else {
        // STA Mode
        doconn.req_type = "WEIO_STA_REQ"
        doconn.load={};
        doconn.load.essid = essid;
        doconn.load.passwd = passwd;

        $('#myModal').modal('hide');
        $('#gone-modal').modal('show');

        //$('#myModalLabel').text('AND WE\'RE GONE...');

        //$("#modcon").attr("disabled", "disabled");
        //$("#input-passwd").hide();
        //$("#modal-footer").hide();
        //$("#modal-x").hide();
    }
    // Will create the JSON string you're looking for.
    var jsonconn = JSON.stringify(doconn);
    sockjs.send(jsonconn);

}

$(window).load(function (){
    App.Conn =  function (essid, encryption){
        if (encryption.trim() == 'on') {
 	        $('#myModalLabel').text('.:: ' + essid + ' ::.')
            //$('#myModal p').text('Network \"' + n + '\" is encrypted - no pass no go ;)');
            //$('#myModal p').text('');
 		    $('#myModal').modal('show');
            $("#modcon").click(function(){
	            console.log('Sending essid and passwd');
                console.log("PSWD : " + $('#input-passwd').val())
	            App.Do(essid, $('#input-passwd').val());
            });
        }
        else {
            // similar behavior as an HTTP redirect
            window.location.replace("http://google.com");

            // similar behavior as clicking on a link
            //window.location.href = "http://stackoverflow.com";
        }
 	}
});
