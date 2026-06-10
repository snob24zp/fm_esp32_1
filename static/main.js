let info = {};
let chunks = [];

// 1. ВАШИ ОРИГИНАЛЬНЫЕ СЛУЖЕБНЫЕ ФУНКЦИИ (БЕЗ ИЗМЕНЕНИЙ)
function $(id) {
    return document.getElementById(id);
}

function get(url, ondone) {
    if (typeof ondone !== "function") return;

    alert("[DEBUG] Сырые данные от платы: " + this.responseText);

    var xhr = new XMLHttpRequest();
    xhr.timeout = 20000;
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            ondone(JSON.parse(this.responseText));
        }
    };
    xhr.open("GET", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(null);
}

function post(url, data, ondone, onerror, timeout) {
    var xhr = new XMLHttpRequest();
    xhr.timeout = timeout === undefined ? 20000 : timeout;
    if (typeof onerror === "function") {
        xhr.ontimeout = onerror;
        xhr.onabort = onerror;
    }
    xhr.onreadystatechange = function () {
        if (this.readyState == 4) {
            if (this.status == 200) {
                if (typeof ondone === "function") ondone(JSON.parse(this.responseText));
            } else {
                if (typeof onerror === "function") onerror(this);
            }
        }
    };
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));
}

function form_to_json() {
    var formElement = document.getElementsByTagName("form")[0];
    if (!formElement) return null;
    var inputElements = Array.from(formElement.getElementsByTagName("input")).filter(inp => inp.type === "text" || inp.type === "password"),
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

// 2. ОРИГИНАЛЬНАЯ ЛОГИКА СТРАНИЦЫ INDEX (WI-FI)
function get_ap_list(ondone) {
    if (typeof ondone !== "function") return;
    var xhr = new XMLHttpRequest();
    xhr.timeout = 20000;
    xhr.ontimeout = function() { get_ap_list(ondone); };
    xhr.onabort = xhr.ontimeout;
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            ondone(JSON.parse(this.responseText));
        }
    };
    xhr.open("GET", "/ap_list", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(null);
}

function append_ap(ap_list) {
    if (ap_list.length > 0) {
        $("ap-list").innerHTML = "";
        for (let ap_name in ap_list) {
            if (ap_list[ap_name]) {
                let div = document.createElement('div');
                div.className = "button title";
                div.innerHTML = `<div class="circle"></div><div class="wifiname"><p class="p1">${ap_list[ap_name]}</p></div>`;
                // Навешиваем клик выбора сети динамически
                div.addEventListener('click', () => {
                    $("ap-name-box").value = ap_list[ap_name];
                });
                $("ap-list").appendChild(div);
            }
        }
    } else {
        setTimeout(() => { get_ap_list(append_ap); }, 20000);
    }
}

function send_ctrl() {
    if (confirm("Do you realy want to set these parameters?")) {
        var _info = form_to_json();
        if (_info === null || `${_info['password']}`.length < 8) {
            alert("Password must be at least 8 symbols length");
            return;
        }
        _info['token'] = info.mac;
        let srv = new URL(window.location).searchParams.get('server');
        if (srv) {
            _info['server'] = `mqtt://${srv}`;
        } else {
            _info['server'] = 'mqtt://x.ks.ua';
        }

        $("main-box").innerHTML = '<h2>Connection establishing..</h2><p class="p1">In <span id="redirect-tmr">60</span> seconds you will be redirected to the main application</p><p class="p1">If this not happend, check Wi-Fi connection and try to reload the page</p>';
        let aA = 60;
        setInterval(function() {
            $("redirect-tmr").innerHTML = aA;
            aA--;
            if (aA == 0) { window.location.href = 'http://swarm.x.ks.ua'; }
        }, 1000);

        var _B = new XMLHttpRequest();
        _B.open('POST', '/ctrl', !0);
        _B.setRequestHeader('Content-Type', 'application/json');
        _B.send(JSON.stringify(_info));
    }
}

// 3. ОРИГИНАЛЬНАЯ ЛОГИКА СТРАНИЦЫ IP
function lock_staticbox() {
    var static_box_inputs = document.querySelectorAll('.box3 input');
    var is_dhcp = $("ip_type").value === 'dhcp';
    static_box_inputs.forEach(inp => {
        if (inp.id !== 'ip_type') { inp.disabled = is_dhcp; }
    });
}

function send_ip_ctrl() {
    if (confirm("Do you realy want to set these parameters?")) {
        let _info = {
            ip_type: $("ip_type").value === 'static' ? 0 : 1,
            ip: $("ip").value,
            mask: $("mask").value,
            gw: $("gw").value,
            dns: $("dns").value
        };
        $("main-box").innerHTML = '<h2>Connection establishing..</h2><p class="p1">In <span id="redirect-tmr">60</span> seconds you will be redirected to the main application</p><p class="p1">If this not happend, check Wi-Fi connection and try to reload the page</p>';
        let aA = 60;
        setInterval(function() {
            $("redirect-tmr").innerHTML = aA;
            aA--;
            if (aA == 0) { window.location.href = 'http://swarm.x.ks.ua'; }
        }, 1000);
        post("/ctrl", _info);
    }
}

// 4. ОРИГИНАЛЬНАЯ ЛОГИКА СТРАНИЦЫ FW (ИЗ СТАРОГО FW.JS)
function file_select(input) {
    let file = input.files[0];
    if (!file) return;
    let reader = new FileReader();
    reader.readAsText(file);
    reader.onload = function () {
        let xml_parser = new DOMParser();
        let xml_data = xml_parser.parseFromString(reader.result, "application/xml");
        if (xml_data.documentElement.nodeName == "parsererror") {
            alert("Can't open FW file");
            return;
        }

        try {
            xml_data = xml_data.documentElement;
            let fw = xml_data.getElementsByTagName("fw")[0];
            $("rst-box").style.top = "180px";
            $("fw_new_built").innerText = fw.getElementsByTagName("built")[0].textContent;
            $("fw_new_type").innerText = fw.getElementsByTagName("type")[0].textContent;
            $("fw_new_ver").innerText = fw.getElementsByTagName("version")[0].textContent;
            $("fw_new_branch").innerText = fw.getElementsByTagName("branch")[0].textContent;
            $("fw_new_commit").innerText = fw.getElementsByTagName("commit")[0].textContent.slice(0, 8);

            let _chunks = xml_data.getElementsByTagName("chunk");
            chunks = [];
            for (let i = 0; i < _chunks.length; i++) {
                chunks.push(_chunks[i].textContent);
            }
            $("upload_file").style.display = "None";
            $("fw_info").style.display = "";
        } catch (e) {
            alert("Wrong file format");
        }
    };
}

function push_chunk(idx, ondone) {
    if (idx >= chunks.length) {
        ondone();
        return;
    }
    $("fw_upl_prg").value = Math.round((idx / chunks.length) * 100);
    $("fw_upl_prg_lbl").innerText = $("fw_upl_prg").value;

    post("/fw_upd", { "idx": idx, "chunk": chunks[idx] }, (_res) => {
        push_chunk(++idx, ondone);
    }, () => {
        push_chunk(idx, ondone);
    });
}

function push_fw() {
    if (confirm("Firmware update process will be started. Device will be rebooted.")) {
        $("rst-box").style.display = "None";
        $("fw_info").style.display = "None";
        $("upload_file").style.display = "None";
        $("write_status").style.display = "";

        post("/fw_upd", 1, (_res) => {
            if (_res === true) {
                push_chunk(0, () => {
                    $("write_status").style.display = "None";
                    $("reboot_status").style.display = "";
                    post("/fw_upd", 2, (_res) => {
                        setTimeout(() => {
                            post("/fw_upd", 3, (_res) => {
                                setTimeout(() => document.location.reload(), 180000);
                            }, () => {
                                setTimeout(() => document.location.reload(), 180000);
                            }, 120000);
                            setTimeout(() => document.location.reload(), 240000);
                        }, 2000);
                    });
                });
            }
        });
    }
}

function rst() {
    if (confirm("Device will be reseted to default configuration")) {
        $("rst-box").style.display = "None";
        $("fw_info").style.display = "None";
        $("upload_file").style.display = "None";
        $("reboot_status").style.display = "";

        post("/reset", parseInt($("serial").innerText), () => {
            $("fw_info").style.display = "None";
            $("write_status").style.display = "None";
            $("reboot_status").style.display = "";
            setTimeout(() => document.location.reload(), 15000);
        });
    }
}

// ============================================================
// 5. АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ И НАВЕШИВАНИЕ СОБЫТИЙ (DOM)
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    const path = window.location.pathname;

    // Шаг 1. Все страницы первым делом запрашивают /info
    get("/info", function (inf) {
        info = inf;
        let ver = inf.version.split(';');
        
        // Общие информационные поля (если они есть на текущей странице)
        if ($("serial")) $("serial").innerText = inf.serial;
        if ($("mac")) $("mac").innerText = inf.mac;
        if ($("ver")) $("ver").innerText = ver[0] + " " + ver[1] + " " + ver[2].slice(0, 8);

        // Шаг 2. Маршрутизация навешивания обработчиков по URL
        
        // --- Логика СТРАНИЦЫ INDEX.HTML (WI-FI) ---
        if (path === '/' || path.includes('index.html')) {
            $("ap-list").innerHTML = "<div class=\"lds-ring\"><div></div><div></div><div></div><div></div></div>";
            get_ap_list(append_ap);

            // Показать/скрыть пароль
            $("pb").addEventListener("click", () => {
                const p = $("pwdbox");
                const type = p.getAttribute('type') === 'password' ? 'text' : 'password';
                p.setAttribute('type', type);
                $("pb").classList.toggle('pbs');
                $("pb").classList.toggle('pbc');
            }, false);

            // Сабмит формы Wi-Fi через перехват события формы
            let form = document.getElementsByTagName("form")[0];
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault(); // отменяем стандартную перезагрузку браузера
                    send_ctrl();
                });
            }
        }

        // --- Логика СТРАНИЦЫ IP.HTML ---
        if (path.includes('ip.html')) {
            $("ip_type").value = info.ip_type === 0 ? 'static' : 'dhcp';
            $("ip").value = info.ip;
            $("gw").value = info.gw;
            $("mask").value = info.mask;
            $("dns").value = info.dns;
            lock_staticbox();

            // Автоматический переключатель disabled полей при смене DHCP/Static
            $("ip_type").addEventListener('change', lock_staticbox);

            // Сабмит формы настроек IP
            let form = document.getElementsByTagName("form")[0];
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    send_ip_ctrl();
                });
            }
        }

        // --- Логика СТРАНИЦЫ FW.HTML (ОБНОВЛЕНИЕ) ---
        if (path.includes('fw.html')) {
            $("fw_cur_type").innerText = info.type;
            $("fw_cur_ver").innerText = ver[0];
            $("fw_cur_branch").innerText = ver[1];
            $("fw_cur_commit").innerText = ver[2];

            // Навешиваем выбор файла на инпут
            let fileInput = document.getElementById("fw-file-input");
            if (fileInput) {
                fileInput.addEventListener('change', function() {
                    file_select(this);
                });
            }

            // Навешиваем клик на кнопку Burn
            let burnBtn = document.getElementById("burn-btn");
            if (burnBtn) {
                burnBtn.addEventListener('click', push_fw);
            }

            // Навешиваем клик на ссылку Reset configuration
            let rstLink = document.getElementById("rst-link");
            if (rstLink) {
                rstLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    rst();
                });
            }
        }
    });
});