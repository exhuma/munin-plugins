var g_cfg = {
    maxDrawWidth: 450,
    drawWidth: 450,
    drawHeight: 110,
    columnWidth: 1,
    xStep: 1,
    uiQosUp: {
        maxValue: 1,
        maxYScale: 0,
        yStep: 4,
        lastValue: [],
        prioClass: [{
            queues: ['realtime', 'hrealtime'],
            color: "#4d6a9b"
        }, {
            queues: ['important'],
            color: "#90bee7"
        }, {
            queues: ['default'],
            color: "#b4e2fe"
        }, {
            queues: ['low'],
            color: "#6fa6d6"
        }]
    },
    uiQosDown: {
        maxValue: 1,
        maxYScale: 0,
        yStep: 4,
        lastValue: [],
        color: ["#f2cc97", "#deb871"]
    }
};
var g_nqos = convertNqosValues({
    "maxUS": "39771",
    "upstream": "333000",
    "numSamples": "20",
    "mcCurrentBps": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
    "sampleInterval": "5",
    "downstream": "5743000",
    "hprio": {
        "enabled": "1",
        "currentBps": "0,0,10048,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    },
    "shapedrate_ds": "0",
    "shapedrate_us": "0",
    "important": {
        "enabled": "1",
        "currentBps": "1770,2003,2416,2607,6519,2851,21899,10048,26044,12412,4642,3148,4992,9317,26521,5512,9359,30846,2077,2120"
    },
    "shapedrate_in_gui": "0",
    "ata": "0",
    "low": {
        "enabled": "1",
        "currentBps": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    },
    "maxDS": "501316",
    "default": {
        "enabled": "1",
        "currentBps": "3211,2448,2660,3593,5883,614,1590,837,614,3296,1038,424,1409,116,1812,2088,233,2120,1600,879"
    },
    "umts": "0",
    "realtime": {
        "enabled": "1",
        "currentBps": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    },
    "dsCurrentBps": "75344,73161,84619,135764,162911,7218,285659,105554,360082,145686,48420,29913,33803,114204,362954,46385,109646,413686,28747,25291",
    "hrealtime": {
        "enabled": "1",
        "currentBps": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    },
    "ifacectl": {
        "enabled": "1",
        "currentBps": "0,21,0,21,0,21,0,21,0,10,0,21,0,21,0,21,0,21,0,21"
    }
})
var g_Timer;
var g_refresh_interval_object = false;
var g_refresh_time = 30000;

function convertNqosValues(obj) {
    obj = obj || {};
    for (var queue in obj) {
        if (typeof obj[queue].enabled != 'undefined') {
            obj[queue].enabled = obj[queue].enabled == "1";
            obj[queue].bps = bpsToIntArray(obj[queue].currentBps || "");
        }
    }
    obj.upstream = parseInt(obj.upstream, 10) || 0;
    obj.downstream = parseInt(obj.downstream, 10) || 0;
    if (obj.shapedrate_in_gui == "1") {
        obj.upstream = Math.min(obj.upstream, 1000 * (parseInt(obj.shapedrate_us, 10) || 0));
        obj.downstream = Math.min(obj.downstream, 1000 * (parseInt(obj.shapedrate_ds, 10) || 0));
    }
    var isDocsis = false;
    if (obj.umts == "1" || obj.ata == "1" || isDocsis) {
        var defaultUpstream = 384000;
        var defaultDownstream = 3600000;
        if (obj.ata == "1") {
            defaultUpstream = 2000000;
            defaultDownstream = 30000000;
        }
        obj.upstream = (8 * parseInt(obj.maxUS, 10)) || defaultUpstream;
        obj.downstream = (8 * parseInt(obj.maxDS, 10)) || defaultDownstream;
        obj.upstream = Math.max(10000, Math.floor(11 * obj.upstream / 10));
        obj.downstream = Math.max(10000, Math.floor(11 * obj.downstream / 10));
    }
    obj.numSamples = parseInt(obj.numSamples, 10) || 1;
    obj.sampleInterval = 1000 * (parseInt(obj.sampleInterval, 10) || 5);
    obj.dsBps = bpsToIntArray(obj.dsCurrentBps || "");
    obj.mcBps = bpsToIntArray(obj.mcCurrentBps || "");
    return obj;
}

function bpsToIntArray(bps) {
    bps = bps.split(",");
    for (var i = 0, len = bps.length; i < len; i++) {
        bps[i] = (parseInt(bps[i], 10) || 0) * 8;
    }
    return bps;
}

function getDSValues(idx, obj) {
    var result = [];
    obj = obj || g_nqos;
    result[0] = g_nqos.dsBps[idx];
    result[1] = g_nqos.mcBps[idx];
    return result;
}

function getPrioClassValues(idx, obj) {
    var result = [];
    var len = g_cfg.uiQosUp.prioClass.length;
    obj = obj || g_nqos;
    for (var i = 0; i < len; i++) {
        result[i] = 0;
        for (var j = 0; j < g_cfg.uiQosUp.prioClass[i].queues.length; j++) {
            var qName = g_cfg.uiQosUp.prioClass[i].queues[j];
            result[i] += obj[qName].bps[idx];
        }
    }
    for (var i = len - 1; i > 0; i--) {
        result[i - 1] += result[i];
    }
    return result;
}

function getFuncColor(divId, idx) {
    if (divId == 'uiQosDown') {
        return g_cfg.uiQosDown.color[idx || 0];
    } else if (divId == 'uiQosUp') {
        return g_cfg.uiQosUp.prioClass[idx].color;
    }
    return "";
}

function getFuncValues(divId, idx) {
    var result = [];
    if (divId == 'uiQosUp') {
        result = getPrioClassValues(idx);
    } else if (divId == 'uiQosDown') {
        result = getDSValues(idx);
    }
    return result;
}

function makeAllValues(divId) {
    var result = [];
    var len = g_nqos.numSamples;
    for (var i = 0; i < len; i++) {
        result[i] = getFuncValues(divId, i);
    }
    return result;
}

function scaleValue(divId, v) {
    var maxStream = 0;
    if (divId == 'uiQosUp') {
        maxStream = g_nqos.upstream;
    } else if (divId == 'uiQosDown') {
        maxStream = g_nqos.downstream;
    }
    v = Math.min(v, maxStream);
    var result = g_cfg.drawHeight * v / g_cfg[divId].maxValue;
    return Math.floor(result);
}

function scaleValues(divId, val) {
    var result = [];
    for (var i = 0; i < val.length; i++) {
        result[i] = scaleValue(divId, val[i]);
    }
    return result;
}

function setLastValues(divId, val) {
    for (var i = 0; i < val.length; i++) {
        g_cfg[divId].lastValue[i] = val[i];
    }
}

function stopTimer() {
    if (g_Timer) {
        window.clearTimeout(g_Timer);
        g_Timer = null;
    }
}

function updateValues() {
    var my_url = "/internet/inetstat_monitor.lua?sid=0180e27f30cd9047&useajax=1&action=get_graphic";
    stopTimer();
    sendUpdateRequest();

    function sendUpdateRequest() {
        ajaxGet(my_url, cbUpdateValues);
    }
    var jsonParse = makeJSONParser();

    function cbUpdateValues(xhr) {
        var txt = xhr.responseText || "null";
        if (xhr.status != 200) {
            txt = "null";
        }
        var newNqos = jsonParse(txt);
        if (!newNqos) {
            return;
        }
        newNqos = convertNqosValues(newNqos);
        var newValueUp = getPrioClassValues(0, newNqos);
        var newValueDown = getDSValues(0, newNqos);
        if (g_nqos.upstream != newNqos.upstream || g_nqos.downstream != newNqos.downstream) {
            setLastValues('uiQosUp', newValueUp);
            setLastValues('uiQosDown', newValueDown);
            g_nqos = newNqos;
            showAllValues();
        } else {
            if (g_cfg.uiQosUp.lastValue.length > 0) {
                showValues('uiQosUp', g_cfg.uiQosUp.lastValue, newValueUp);
            }
            if (g_cfg.uiQosDown.lastValue.length > 0) {
                showValues('uiQosDown', g_cfg.uiQosDown.lastValue, newValueDown);
            }
            setLastValues('uiQosUp', newValueUp);
            setLastValues('uiQosDown', newValueDown);
            g_nqos = newNqos;
        }
        g_Timer = window.setTimeout(sendUpdateRequest, g_nqos.sampleInterval);
    }
}

function clearValues(divId) {
    var divQoS = jxl.get(divId);
    if (divQoS) {
        divQoS.innerHTML = "";
    }
}

function isColumn(el) {
    return jxl.hasClass(el, "column");
}

function dropFirstColumns(parentDiv) {
    var columns = jxl.walkDom(parentDiv, 'div', isColumn);
    if (columns && columns.length) {
        var cnt = columns.length - g_nqos.numSamples + 2;
        for (var i = 0; i < cnt; i++) {
            if (columns[i]) {
                parentDiv.removeChild(columns[i]);
            }
        }
    }
}

function showValues(divId, leftValue, rightValue) {
    leftValue = scaleValues(divId, leftValue);
    rightValue = scaleValues(divId, rightValue);
    var divQoS = jxl.get(divId);
    dropFirstColumns(divQoS);
    var columnDiv = document.createElement('div');
    columnDiv.className = "column";
    columnDiv.style.width = g_cfg.columnWidth + "px";
    var valDiv = [];
    for (var i = 0, len = leftValue.length; i < len; i++) {
        valDiv[i] = document.createElement('div');
        valDiv[i].className = "func";
        valDiv[i].style.height = "" + Math.min(rightValue[i], leftValue[i]) + "px";
        valDiv[i].style.borderTopWidth = "" + Math.abs(rightValue[i] - leftValue[i]) + "px";
        var side = leftValue[i] < rightValue[i] ? "Right" : "Left";
        valDiv[i].style["border" + side + "Width"] = g_cfg.columnWidth + "px";
        valDiv[i].style["border" + side + "Color"] = getFuncColor(divId, i);
        columnDiv.appendChild(valDiv[i]);
    }
    divQoS.appendChild(columnDiv);
}

function allDivsStr(divId, onlyInside) {
    var funcStr;
    if (divId == "uiQosUp") {
        funcStr = upstreamFuncStr;
    } else if (divId == "uiQosDown") {
        funcStr = downstreamFuncStr;
    }
    calcDrawValues();
    var val = makeAllValues(divId);
    var str = [];
    if (!onlyInside) {
        str.push("<div id=\"" + divId + "\" class=\"qos\"");
        str.push(" style=\"width:" + g_cfg.drawWidth + "px;\">");
    }
    for (var i = g_nqos.numSamples - 1; i > 0; i--) {
        str.push(funcStr(val[i], val[i - 1]));
    }
    if (!onlyInside) {
        str.push("</div>");
    }
    return str.join("");;
}

function upstreamFuncStr(leftValue, rightValue) {
    var str = [];
    var divId = 'uiQosUp';
    leftValue = scaleValues(divId, leftValue);
    rightValue = scaleValues(divId, rightValue);
    str.push("<div class=\"column\"");
    str.push(" style=\"width:" + g_cfg.columnWidth + "px;");
    str.push("\">");
    for (var i = 0, len = leftValue.length; i < len; i++) {
        str.push("<div class=\"func\" style=\"");
        str.push("height:" + Math.min(rightValue[i], leftValue[i]) + "px;");
        str.push("border-top-width:" + Math.abs(rightValue[i] - leftValue[i]) + "px;");
        var side = leftValue[i] < rightValue[i] ? "right" : "left";
        str.push("border-" + side + "-width:" + g_cfg.columnWidth + "px;");
        str.push("border-" + side + "-color:" + getFuncColor(divId, i) + ";");
        str.push("\"></div>");
    }
    str.push("</div>");
    return str.join("");
}

function downstreamFuncStr(leftValue, rightValue) {
    var str = [];
    var divId = 'uiQosDown';
    leftValue = scaleValues(divId, leftValue);
    rightValue = scaleValues(divId, rightValue);
    str.push("<div class=\"column\"");
    str.push(" style=\"width:" + g_cfg.columnWidth + "px;");
    str.push("\">");
    for (var i = 0, len = leftValue.length; i < len; i++) {
        str.push("<div class=\"func\" style=\"");
        str.push("height:" + Math.min(rightValue[i], leftValue[i]) + "px;");
        str.push("border-top-width:" + Math.abs(rightValue[i] - leftValue[i]) + "px;");
        var side = leftValue[i] < rightValue[i] ? "right" : "left";
        str.push("border-" + side + "-width:" + g_cfg.columnWidth + "px;");
        str.push("border-" + side + "-color:" + getFuncColor(divId, i) + ";");
        str.push("\"></div>");
    }
    str.push("</div>");
    return str.join("");
}

function calcMaxValue(divId) {
    if (divId == 'uiQosUp') {
        g_cfg[divId].maxValue = Math.max(1, g_nqos.upstream);
    } else if (divId == 'uiQosDown') {
        g_cfg[divId].maxValue = Math.max(1, g_nqos.downstream);
    }
    if (g_cfg[divId].maxValue == 1) {
        g_cfg[divId].maxYScale = 0;
    }
    var d = 100000;
    while (g_cfg[divId].maxValue < d) {
        d /= 10;
    }
    g_cfg[divId].maxYScale = Math.floor(g_cfg[divId].maxValue / d) * d;
    while (scaleValue(divId, g_cfg[divId].maxValue) - scaleValue(divId, g_cfg[divId].maxYScale) < 15) {
        g_cfg[divId].maxYScale -= d;
    }
}

function calcDrawValues() {
    var w = g_cfg.maxDrawWidth;
    var n = g_nqos.numSamples - 1;
    var c = Math.floor(Math.max(1, w / n));
    while (c > 1 && n * c < w) {
        w--;
        c = Math.floor(Math.max(1, w / n));
    }
    g_cfg.drawWidth = w;
    g_cfg.columnWidth = c;
    calcMaxValue('uiQosUp');
    calcMaxValue('uiQosDown');
}

function numToStr3(num) {
    var prefix = "";
    if (num < 100) {
        prefix += "0";
    }
    if (num < 10) {
        prefix += "0";
    }
    return prefix + num;
}

function dottedStr(num) {
    var result = [];
    var z = parseInt(num, 10);
    while (z > 999) {
        result.push(numToStr3(z % 1000));
        z = Math.floor(z / 1000);
    }
    result.push(z);
    return result.reverse().join(".");
}

function yScaleStr(divId) {
    var v = [];
    if (g_cfg[divId].maxValue <= 1) {
        v[0] = 0;
    } else {
        for (var i = g_cfg[divId].yStep; i >= 0; i--) {
            v[i] = i * g_cfg[divId].maxYScale / g_cfg[divId].yStep;
        }
    }
    var str = [];
    if (g_cfg[divId].maxValue > 1) {
        str.push('<div style=\"bottom:' + (g_cfg.drawHeight + 1) + 'px;\">');
        str.push('<span class=\"number\">' + dottedStr(g_cfg[divId].maxValue / 1000) + '</span>');
        str.push('<span class=\"scale\"></span>');
        str.push('</div>');
    }
    for (var i = 0; i < v.length; i++) {
        var b = Math.floor(g_cfg.drawHeight * v[i] / g_cfg[divId].maxValue);
        str.push('<div style=\"bottom:' + b + 'px;\">');
        str.push('<span class=\"number\">' + dottedStr(v[i] / 1000) + '</span>');
        str.push('<span class=\"scale\"></span>');
        str.push('</div>');
    }
    return str.join("");
}

function showYScale(divId) {
    var divYScale = jxl.get(divId + "YScale");
    var div = [];
    var v = [];
    if (g_cfg[divId].maxValue <= 1) {
        v[0] = 0;
    } else {
        for (var i = g_cfg[divId].yStep; i >= 0; i--) {
            v[i] = i * g_cfg[divId].maxYScale / g_cfg[divId].yStep;
        }
    }
    var inc = 0;
    if (g_cfg[divId].maxValue > 1) {
        div[0] = document.createElement('div');
        var b = Math.floor(g_cfg.drawHeight);
        div[0].style.bottom = b + "px";
        var span = document.createElement('span');
        span.className = "number";
        span.innerHTML = dottedStr(g_cfg[divId].maxValue / 1000);
        div[0].appendChild(span);
        span = document.createElement('span');
        span.className = "scale";
        div[0].appendChild(span);
        inc = 1;
    }
    for (var i = 0; i < v.length; i++) {
        div[i + inc] = document.createElement('div');
        var b = Math.floor(g_cfg.drawHeight * v[i] / g_cfg[divId].maxValue);
        div[i + inc].style.bottom = b + "px";
        var span = document.createElement('span');
        span.className = "number";
        span.innerHTML = dottedStr(v[i] / 1000);
        div[i + inc].appendChild(span);
        span = document.createElement('span');
        span.className = "scale";
        div[i + inc].appendChild(span);
    }
    divYScale.innerHTML = "";
    var fragment = document.createDocumentFragment();
    for (var i = 0; i < div.length; i++) {
        fragment.appendChild(div[i]);
    }
    divYScale.appendChild(fragment);
}

function showAllValues() {
    var div = document.getElementById("uiQosDown");
    div.innerHTML = allDivsStr("uiQosDown", true);
    div = document.getElementById("uiQosDownYScale");
    div.innerHTML = yScaleStr('uiQosDown');
    div = document.getElementById("uiQosUp");
    div.innerHTML = allDivsStr("uiQosUp", true);
    div = document.getElementById("uiQosUpYScale");
    div.innerHTML = yScaleStr('uiQosUp');
}

function change_time_interval_ajax(refresh_time) {
    if (g_refresh_interval_object) window.clearInterval(g_refresh_interval_object);
    g_refresh_interval_object = window.setInterval(RefreshPageContent, refresh_time);
}

function RefreshPageContent(part) {
    var my_url = "/internet/inetstat_monitor.lua?sid=0180e27f30cd9047&useajax=1&action=get_table";
    sendUpdateRequest();

    function sendUpdateRequest() {
        ajaxGet(my_url, cbUpdateTable);
    }

    function cbUpdateTable(xhr) {
        var txt = xhr.responseText || "null";
        if (xhr.status != 200) {
            return;
        }
        jxl.setHtml("uiInternetMonitor", txt)
        zebra();
        var obj = document.getElementById("uiConnectState")
        if (obj && obj.value == "5") {
            jxl.enable("uiReconnectBtn");
        }
    }
}

function uiDoRefresh() {
    if (g_refresh_interval_object) {
        window.clearInterval(g_refresh_interval_object);
    }
    if (g_Timer) {
        window.clearTimeout(g_Timer);
    }
    location.href = ""
}

function connect_again() {
    var my_url = "/internet/inetstat_monitor.lua?sid=0180e27f30cd9047&useajax=1&action=connect";
    sendUpdateRequest();

    function sendUpdateRequest() {
        ajaxGet(my_url, cbConnected);
    }

    function cbConnected() {
        jxl.enable("uiReconnectBtn");
        jxl.hide("uiWarnDisconnecting");
        RefreshPageContent();
        change_time_interval_ajax(g_refresh_time);
    }
}

function DoDisconnectInternet() {
    var my_url = "/internet/inetstat_monitor.lua?sid=0180e27f30cd9047&useajax=1&action=disconnect";
    sendUpdateRequest();

    function sendUpdateRequest() {
        change_time_interval_ajax(2000);
        jxl.disable("uiReconnectBtn");
        jxl.show("uiWarnDisconnecting");
        ajaxGet(my_url, cbDisconnected);
    }

    function cbDisconnected() {
        window.setTimeout("connect_again()", 6000);
        window.setTimeout(function () {
            change_time_interval_ajax(g_refresh_time);
        }, 60000);
    }
    return false;
}

function init() {
    updateValues()
    if (g_refresh_interval_object) window.clearInterval(g_refresh_interval_object);
    RefreshPageContent();
    g_refresh_interval_object = window.setInterval(RefreshPageContent, g_refresh_time);
    window.setTimeout(uiDoRefresh, 60 * 60 * 1000);
}
ready.onReady(init);
