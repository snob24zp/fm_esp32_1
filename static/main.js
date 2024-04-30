let tmr_upd_time = 4000;
let info = {}

function $(id) {
    return document.getElementById(id)
}

function get(url, ondone) {
    if (typeof ondone !== "function") {
        return
    }
    var xhr = new XMLHttpRequest();
    xhr.timeout = 30000;
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            ondone(JSON.parse(this.responseText));
        }
    };

    xhr.open("GET", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(null)
}


function form_to_json() {
    var formElement = document.getElementsByTagName("form")[0],
        inputElements = Array.from(formElement.getElementsByTagName("input")).filter(inp => inp.type ===
            "text" || inp.type === "password"),
        jsonObject = {};

    for (var i = 0; i < inputElements.length; i++) {
        var inputElement = inputElements[i];
        if (inputElement.type === "text" && !inputElement.validity.valid) {
            return null;
        }
        jsonObject[inputElement.name] = inputElement.value;
    }
    return jsonObject;
}

function send_ctrl() {
    if (confirm("Do you realy want to set these parameters?")) {
        var obj = form_to_json();

        if (obj === null) {
            return
        }
        obj['token'] = info.mac;
        srv = new URL(window.location).searchParams.get('server')
        if (srv) {
            console.log('Will use server: ', srv)
            obj['server'] = "mqtt://" + srv
        } else {
            obj['server'] = "mqtt://x.ks.ua"
        }

        $("main-box").innerHTML = "<h2>Connection establishing..</h2>\
                            <p class=\"p1\">In <span id=\"redirect-tmr\">60</span> seconds you will be redirected to the main application</p>\
                            <p class=\"p1\">If this not happend, check Wi-Fi connection and try to reload the page</p>";

        let redir_cnt = 60;
        setInterval(function () {
            $("redirect-tmr").innerHTML = redir_cnt
            redir_cnt--;
            if (redir_cnt == 0) {
                window.location.href = "http://swarm.x.ks.ua"
            }
        }, 1000);

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/ctrl", true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(obj));
    }
}

function get_ap_list(ondone) {
    if (typeof ondone !== "function") {
        return
    }
    var xhr = new XMLHttpRequest();
    xhr.timeout = 30000;
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            ondone(JSON.parse(this.responseText));
        }
    };

    xhr.open("GET", "/ap_list", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(null)
}

function set_ap_name(name) {
    $("ap-name-box").value = name;
}

function append_ap(ap_list) {
    console.log(ap_list);
    if (ap_list.length > 0) {
        $("ap-list").innerHTML = "";
        for (let ap_name in ap_list) {
            if (ap_list[ap_name]) {
                $("ap-list").innerHTML +=
                    "<div class=\"button title\" onclick='set_ap_name(\"" + ap_list[ap_name] + "\");'>\
                            <div class=\"circle\"></div>\
                            <div class=\"wifiname\">\
                            <p class=\"p1\">" + ap_list[ap_name] + "</p>\
                            </div></div>\
                            <hr>";
            }
        }
        tmr_upd_time = 30000;
    } else {
        setTimeout(function () { get_ap_list(append_ap) }, 10000);
    }
}

function lock_staticbox() {
    for (let el of document.querySelectorAll(".box3 input")) {
        el.disabled = $("ip_type").options.selectedIndex == 1;
    }
}
