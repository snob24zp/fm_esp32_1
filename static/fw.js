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

let chunks = []

function file_select(input) {
    let file = input.files[0];
    let reader = new FileReader();
    reader.readAsText(file);
    reader.onload = function () {
        let xml_parser = new DOMParser();
        let xml_data = xml_parser.parseFromString(reader.result, "application/xml");
        if (xml_data.documentElement.nodeName == "parsererror") {
            alert("Can't open FW file")
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
            alert("Can't open FW file")
        }
    };

    reader.onerror = function () {
        alert("Can't open FW file: " + reader.error);
    };
}

function post(uri, data, ondone, onerror, timeout = 30000) {
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
                alert("Error updating device firmware")
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
                        post("/fw_upd", 3, (_res) => {
                            console.log("Done", _res)
                            setTimeout(() => document.location.reload(), 180000);
                        }, ()=>{
                            console.log("Error happend")
                            setTimeout(() => document.location.reload(), 180000);
                        }, 120000);

                        setTimeout(() => document.location.reload(), 240000);
                    }, 2000)
                })
            }
        })
    }
}

function rst() {
    if (confirm("Device will be reseted to default configuration")) {
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

