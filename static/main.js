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
    if (confirm("Установить выбранные параметры?")) {
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

        $("main-box").innerHTML = "<h2>Подключение..</h2>\
                            <p class=\"p1\">Через <span id=\"redirect-tmr\">60</span> секунд вы перейдете на сайт для дальнейшей настройки</p>\
                            <p class=\"p1\">Если этого не произошло, проверьте список WIFI сетей</p>";

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



let chunks = []

function file_select(input) {
    let file = input.files[0];
    let reader = new FileReader();
    reader.readAsText(file);
    reader.onload = function () {
        let xml_parser = new DOMParser();
        let xml_data = xml_parser.parseFromString(reader.result, "application/xml");
        if (xml_data.documentElement.nodeName == "parsererror") {
            alert("Ошибка открытия файла ПО")
            return
        }

        try {
            xml_data = xml_data.documentElement
            let fw = xml_data.getElementsByTagName("fw")[0]
            $("rst-box").style.top = "415px";
            $("fw_new_built").innerText = fw.getElementsByTagName("date")[0].innerHTML
            $("fw_new_type").innerText = fw.getElementsByTagName("device")[0].innerHTML
            $("fw_new_ver").innerText = fw.getElementsByTagName("version")[0].innerHTML
            try {
                $("fw_new_branch").innerText = fw.getElementsByTagName("branch")[0].innerHTML
                $("fw_new_commit").innerText = fw.getElementsByTagName("commit")[0].innerHTML
            } catch (e) {
                console.log("FW File does not contains git information:", e)
                $("fw_new_branch").innerText = " - "
                $("fw_new_commit").innerText = " - "
            }

            let _chunks = xml_data.getElementsByTagName("chunks")[0].childNodes

            for (var i = 0; i < _chunks.length; i++) {
                if (_chunks[i].nodeType == Node.ELEMENT_NODE) {
                    chunks.push(_chunks[i].textContent)
                }
            }

            $("upload_file").style.display = "None";
            $("fw_info").style.display = "";

        } catch (e) {
            alert("Ошибка открытия файла ПО")
        }
    };

    reader.onerror = function () {
        alert("Ошибка открытия файла: " + reader.error);
    };
}

function post(uri, data, ondone, onerror) {
    var xhr = new XMLHttpRequest();
    xhr.timeout = 30000;
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200 && typeof ondone === "function") {
            try {
                ondone(JSON.parse(this.responseText));
            } catch {
                onerror()
            }
        }

        if (this.readyState == 4 && this.status != 200 && typeof onerror === "function") {
            onerror()
        }

    };
    xhr.open("POST", uri, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data))
}

function push_fw() {
    $("rst-box").style.display = "None";
    $("fw_info").style.display = "None";
    $("write_status").style.display = "";
    let err_cnt = 0
    let len = chunks.length
    if (len > 0) {
        post("/fw_upd", 1, function snd(res) {
            let idx = res === 'OK' ? 0 : res.chunk
            ch = chunks[idx]
            console.log("response: ", res)
            if (err_cnt > 10) {
                alert("Ошибка обновления ПО, обратитесь в тех поддержку")
                return
            }
            set_upl_progress(Number((idx / len) * 100).toFixed(2))
            if (ch) {
                post("/fw_pkg", ch, (r) => {
                    snd(r);
                    err_cnt = 0
                }, () => {
                    console.log("Resend: ", err_cnt)
                    snd(res);
                    err_cnt++
                })
            } else {
                $("write_status").style.display = "None";
                $("reboot_status").style.display = "";
                console.log("Upgrade and reboot")
                post("/fw_upd", 2, (_res) => {
                    console.log("response: ", res)
                    setTimeout(() => {
                        post("/fw_upd", 3, () => {
                            setTimeout(() => document.location.reload(), 1000)
                        })
                    }, 5000)
                })
            }
        })
    }
}

function rst() {
    if (confirm("Устройство будет сброшено по-умолчанию, продолжить?")) {
        console.log("Upgrade and reboot")
        $("rst-box").style.display = "None";
        $("fw_info").style.display = "None";
        $("upload_file").style.display = "None";
        $("reboot_status").style.display = "";

        post("/reset", parseInt($("serial").innerText), () => {
            $("fw_info").style.display = "None";
            $("write_status").style.display = "None";
            $("reboot_status").style.display = "";
            setTimeout(() => document.location.reload(), 15000)
        });
    }
}

function set_upl_progress(val) {
    $("fw_upl_prg").value = val
    $("fw_upl_prg_lbl").innerText = val
}

