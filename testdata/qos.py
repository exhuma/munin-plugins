from math import floor

g_cfg = {
    'maxDrawWidth': 450,
    'drawWidth': 450,
    'drawHeight': 110,
    'columnWidth': 1,
    'xStep': 1,
    'uiQosUp': {
        'maxValue': 1,
        'maxYScale': 0,
        'yStep': 4,
        'lastValue': [],
        'prioClass': [{
            'queues': ['realtime', 'hrealtime'],
            'color': "#4d6a9b"
        }, {
            'queues': ['important'],
            'color': "#90bee7"
        }, {
            'queues': ['default'],
            'color': "#b4e2fe"
        }, {
            'queues': ['low'],
            'color': "#6fa6d6"
        }]
    },
    'uiQosDown': {
        'maxValue': 1,
        'maxYScale': 0,
        'yStep': 4,
        'lastValue': [],
        'color': ["#f2cc97", "#deb871"]
    }
}

g_nqos = convertNqosValues({
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
        "currentBps": ("1770,2003,2416,2607,6519,2851,21899,10048,26044,12412,"
                       "4642,3148,4992,9317,26521,5512,9359,30846,2077,2120")
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
        "currentBps": ("3211,2448,2660,3593,5883,614,1590,837,614,3296,1038,"
                       "424,1409,116,1812,2088,233,2120,1600,879")
    },
    "umts": "0",
    "realtime": {
        "enabled": "1",
        "currentBps": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    },
    "dsCurrentBps": ("75344,73161,84619,135764,162911,7218,285659,105554,"
                     "360082,145686,48420,29913,33803,114204,362954,46385,"
                     "109646,413686,28747,25291"),
    "hrealtime": {
        "enabled": "1",
        "currentBps": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    },
    "ifacectl": {
        "enabled": "1",
        "currentBps": "0,21,0,21,0,21,0,21,0,10,0,21,0,21,0,21,0,21,0,21"
    }
})

g_Timer = None
g_refresh_interval_object = False
g_refresh_time = 30000


def convertNqosValues(obj):
    newobj = obj.copy() if obj else {}

    for key in obj:
        if isinstance(obj[key], dict) and 'enabled' in obj[key]:
            newobj[key]['enabled'] = obj[key]['enabled'] == '1'
            newobj[key]['bps'] = bps_to_int_array(
                obj[key].get('currentBps', ''))

    newobj['upstream'] = int(obj.get('upstream', 0))
    newobj['downstream'] = int(obj.get('downstream', 0))
    if obj['shapedrate_in_gui'] == "1":
        newobj['upstream'] = min(newobj['upstream'],
                                 1000 * (int(obj.get('shapedrate_us'), 0)))
        newobj['downstream'] = min(newobj['downstream'],
                                   1000 * (int(obj.get('shapedrate_ds'), 0)))

    isDocsis = False
    if (obj['umts'] == "1" or obj['ata'] == "1" or isDocsis):
        defaultUpstream = 384000
        defaultDownstream = 3600000
        if obj['ata'] == "1":
            defaultUpstream = 2000000
            defaultDownstream = 30000000

        try:
            newobj['upstream'] = (8 * int(obj['maxUS']))
        except:
            newobj['upstream'] = defaultUpstream

        try:
            newobj['downstream'] = (8 * int(obj['maxDS']))
        except:
            newobj['downstream'] = defaultDownstream

        newobj['upstream'] = max(10000,
                                 floor(11 * newobj['upstream'] / 10.0))
        newobj['downstream'] = max(10000,
                                   floor(11 * newobj['downstream'] / 10.0))

    newobj['numSamples'] = int(obj.get('numSamples'), 1)
    newobj['sampleInterval'] = 1000 * (int(obj.get('sampleInterval'), 5))
    newobj['dsBps'] = bpsToIntArray(obj.get('dsCurrentBps', ''))
    newobj['mcBps'] = bpsToIntArray(obj.get('mcCurrentBps', ''))
    return newobj


def bpsToIntArray(bps):
    bps = bps.split(",")
    out = []
    for val in bps:
        try:
            val = int(val)
        except ValueError:
            val = 0
        out.append(8 * val)

    return out


def getDSValues(idx, obj):
    obj = obj or g_nqos
    return g_nqos.dsBps[idx], g_nqos.mcBps[idx]


def getPrioClassValues(idx, obj):
    result = []
    obj = obj or g_nqos

    for x in g_cfg.uiQosUp.prioClass:
        val = 0
        for qName in x.queues:
            val += obj[qName].bps[idx]
        result.append(x)

    i = len(result) - 1
    while i > 0:
        result[i - 1] += result[i]
        i -= 1

    return result


def getFuncColor(divId, idx):
    if (divId == 'uiQosDown'):
        return g_cfg.uiQosDown.color[idx or 0]
    elif divId == 'uiQosUp':
        return g_cfg.uiQosUp.prioClass[idx].color

    return ""


def getFuncValues(divId, idx):
    result = []
    if divId == 'uiQosUp':
        result = getPrioClassValues(idx)
    elif divId == 'uiQosDown':
        result = getDSValues(idx)
    return result


def makeAllValues(divId):
    result = []
    len = g_nqos.numSamples
    for i, _ in enumerate(g_nqos.numSamples):
        result.append(getFuncValues(divId, i))
    return result


def scaleValue(divId, v):
    maxStream = 0
    if divId == 'uiQosUp':
        maxStream = g_nqos.upstream
    elif divId == 'uiQosDown':
        maxStream = g_nqos.downstream

    v = min(v, maxStream)
    result = g_cfg.drawHeight * v / float(g_cfg[divId].maxValue)
    return floor(result)


def scaleValues(divId, val):
    result = []
    for value in val:
        result.append(scaleValue(divId, value))
    return result


def setLastValues(divId, val):
    for i, value in val:
        g_cfg[divId].lastValue[i] = value


def updateValues():
    my_url = "/internet/inetstat_monitor.lua?sid=0180e27f30cd9047&useajax=1&action=get_graphic"
    stopTimer()
    sendUpdateRequest()

    def sendUpdateRequest():
        ajaxGet(my_url, cbUpdateValues)
    jsonParse = makeJSONParser()

    def cbUpdateValues(xhr):
        txt = xhr.responseText or "null"
        if (xhr.status != 200) {
            txt = "null"
        }
        newNqos = jsonParse(txt)
        if (!newNqos) {
            return
        }
        newNqos = convertNqosValues(newNqos)
        newValueUp = getPrioClassValues(0, newNqos)
        newValueDown = getDSValues(0, newNqos)
        if (g_nqos.upstream != newNqos.upstream or g_nqos.downstream != newNqos.downstream) {
            setLastValues('uiQosUp', newValueUp)
            setLastValues('uiQosDown', newValueDown)
            g_nqos = newNqos
            showAllValues()
        } else {
            if (g_cfg.uiQosUp.lastValue.length > 0) {
                showValues('uiQosUp', g_cfg.uiQosUp.lastValue, newValueUp)
            }
            if (g_cfg.uiQosDown.lastValue.length > 0) {
                showValues('uiQosDown', g_cfg.uiQosDown.lastValue, newValueDown)
            }
            setLastValues('uiQosUp', newValueUp)
            setLastValues('uiQosDown', newValueDown)
            g_nqos = newNqos
        }
        g_Timer = window.setTimeout(sendUpdateRequest, g_nqos.sampleInterval)

def clearValues(divId):
    divQoS = jxl.get(divId)
    if (divQoS) {
        divQoS.innerHTML = ""
    }

def isColumn(el):
    return jxl.hasClass(el, "column")

def dropFirstColumns(parentDiv):
    columns = jxl.walkDom(parentDiv, 'div', isColumn)
    if (columns and columns.length) {
        cnt = columns.length - g_nqos.numSamples + 2
        for (var i = 0; i < cnt; i++) {
            if (columns[i]) {
                parentDiv.removeChild(columns[i])
            }
        }
    }

def showValues(divId, leftValue, rightValue):
    leftValue = scaleValues(divId, leftValue)
    rightValue = scaleValues(divId, rightValue)
    divQoS = jxl.get(divId)
    dropFirstColumns(divQoS)
    columnDiv = document.createElement('div')
    columnDiv.className = "column"
    columnDiv.style.width = g_cfg.columnWidth + "px"
    valDiv = []
    for (var i = 0, len = leftValue.length; i < len; i++) {
        valDiv[i] = document.createElement('div')
        valDiv[i].className = "func"
        valDiv[i].style.height = "" + min(rightValue[i], leftValue[i]) + "px"
        valDiv[i].style.borderTopWidth = "" + abs(rightValue[i] - leftValue[i]) + "px"
        side = leftValue[i] < rightValue[i] ? "Right" : "Left"
        valDiv[i].style["border" + side + "Width"] = g_cfg.columnWidth + "px"
        valDiv[i].style["border" + side + "Color"] = getFuncColor(divId, i)
        columnDiv.appendChild(valDiv[i])
    }
    divQoS.appendChild(columnDiv)

def allDivsStr(divId, onlyInside):
    funcStr
    if (divId == "uiQosUp") {
        funcStr = upstreamFuncStr
    } else if (divId == "uiQosDown") {
        funcStr = downstreamFuncStr
    }
    calcDrawValues()
    val = makeAllValues(divId)
    str = []
    if (!onlyInside) {
        str.push("<div id=\"" + divId + "\" class=\"qos\"")
        str.push(" style=\"width:" + g_cfg.drawWidth + "px;\">")
    }
    for (var i = g_nqos.numSamples - 1; i > 0; i--) {
        str.push(funcStr(val[i], val[i - 1]))
    }
    if (!onlyInside) {
        str.push("</div>")
    }
    return str.join("");

def upstreamFuncStr(leftValue, rightValue):
    str = []
    divId = 'uiQosUp'
    leftValue = scaleValues(divId, leftValue)
    rightValue = scaleValues(divId, rightValue)
    str.push("<div class=\"column\"")
    str.push(" style=\"width:" + g_cfg.columnWidth + "px;")
    str.push("\">")
    for (var i = 0, len = leftValue.length; i < len; i++) {
        str.push("<div class=\"func\" style=\"")
        str.push("height:" + min(rightValue[i], leftValue[i]) + "px;")
        str.push("border-top-width:" + abs(rightValue[i] - leftValue[i]) + "px;")
        side = leftValue[i] < rightValue[i] ? "right" : "left"
        str.push("border-" + side + "-width:" + g_cfg.columnWidth + "px;")
        str.push("border-" + side + "-color:" + getFuncColor(divId, i) + ";")
        str.push("\"></div>")
    }
    str.push("</div>")
    return str.join("")

def downstreamFuncStr(leftValue, rightValue):
    str = []
    divId = 'uiQosDown'
    leftValue = scaleValues(divId, leftValue)
    rightValue = scaleValues(divId, rightValue)
    str.push("<div class=\"column\"")
    str.push(" style=\"width:" + g_cfg.columnWidth + "px;")
    str.push("\">")
    for (var i = 0, len = leftValue.length; i < len; i++) {
        str.push("<div class=\"func\" style=\"")
        str.push("height:" + min(rightValue[i], leftValue[i]) + "px;")
        str.push("border-top-width:" + abs(rightValue[i] - leftValue[i]) + "px;")
        side = leftValue[i] < rightValue[i] ? "right" : "left"
        str.push("border-" + side + "-width:" + g_cfg.columnWidth + "px;")
        str.push("border-" + side + "-color:" + getFuncColor(divId, i) + ";")
        str.push("\"></div>")
    }
    str.push("</div>")
    return str.join("")

def calcMaxValue(divId):
    if (divId == 'uiQosUp') {
        g_cfg[divId].maxValue = max(1, g_nqos.upstream)
    } else if (divId == 'uiQosDown') {
        g_cfg[divId].maxValue = max(1, g_nqos.downstream)
    }
    if (g_cfg[divId].maxValue == 1) {
        g_cfg[divId].maxYScale = 0
    }
    d = 100000
    while (g_cfg[divId].maxValue < d) {
        d /= 10
    }
    g_cfg[divId].maxYScale = floor(g_cfg[divId].maxValue / d) * d
    while (scaleValue(divId, g_cfg[divId].maxValue) - scaleValue(divId, g_cfg[divId].maxYScale) < 15) {
        g_cfg[divId].maxYScale -= d
    }

def calcDrawValues():
    w = g_cfg.maxDrawWidth
    n = g_nqos.numSamples - 1
    c = floor(max(1, w / n))
    while (c > 1 and n * c < w) {
        w--
        c = floor(max(1, w / n))
    }
    g_cfg.drawWidth = w
    g_cfg.columnWidth = c
    calcMaxValue('uiQosUp')
    calcMaxValue('uiQosDown')

def numToStr3(num):
    prefix = ""
    if (num < 100) {
        prefix += "0"
    }
    if (num < 10) {
        prefix += "0"
    }
    return prefix + num

def dottedStr(num):
    result = []
    z = int(num)
    while (z > 999) {
        result.push(numToStr3(z % 1000))
        z = floor(z / 1000)
    }
    result.push(z)
    return result.reverse().join(".")

def yScaleStr(divId):
    v = []
    if (g_cfg[divId].maxValue <= 1) {
        v[0] = 0
    } else {
        for (var i = g_cfg[divId].yStep; i >= 0; i--) {
            v[i] = i * g_cfg[divId].maxYScale / g_cfg[divId].yStep
        }
    }
    str = []
    if (g_cfg[divId].maxValue > 1) {
        str.push('<div style=\"bottom:' + (g_cfg.drawHeight + 1) + 'px;\">')
        str.push('<span class=\"number\">' + dottedStr(g_cfg[divId].maxValue / 1000) + '</span>')
        str.push('<span class=\"scale\"></span>')
        str.push('</div>')
    }
    for (var i = 0; i < v.length; i++) {
        b = floor(g_cfg.drawHeight * v[i] / g_cfg[divId].maxValue)
        str.push('<div style=\"bottom:' + b + 'px;\">')
        str.push('<span class=\"number\">' + dottedStr(v[i] / 1000) + '</span>')
        str.push('<span class=\"scale\"></span>')
        str.push('</div>')
    }
    return str.join("")

def showYScale(divId):
    divYScale = jxl.get(divId + "YScale")
    div = []
    v = []
    if (g_cfg[divId].maxValue <= 1) {
        v[0] = 0
    } else {
        for (var i = g_cfg[divId].yStep; i >= 0; i--) {
            v[i] = i * g_cfg[divId].maxYScale / g_cfg[divId].yStep
        }
    }
    inc = 0
    if (g_cfg[divId].maxValue > 1) {
        div[0] = document.createElement('div')
        b = floor(g_cfg.drawHeight)
        div[0].style.bottom = b + "px"
        span = document.createElement('span')
        span.className = "number"
        span.innerHTML = dottedStr(g_cfg[divId].maxValue / 1000)
        div[0].appendChild(span)
        span = document.createElement('span')
        span.className = "scale"
        div[0].appendChild(span)
        inc = 1
    }
    for (var i = 0; i < v.length; i++) {
        div[i + inc] = document.createElement('div')
        b = floor(g_cfg.drawHeight * v[i] / g_cfg[divId].maxValue)
        div[i + inc].style.bottom = b + "px"
        span = document.createElement('span')
        span.className = "number"
        span.innerHTML = dottedStr(v[i] / 1000)
        div[i + inc].appendChild(span)
        span = document.createElement('span')
        span.className = "scale"
        div[i + inc].appendChild(span)
    }
    divYScale.innerHTML = ""
    fragment = document.createDocumentFragment()
    for (var i = 0; i < div.length; i++) {
        fragment.appendChild(div[i])
    }
    divYScale.appendChild(fragment)

def showAllValues():
    div = document.getElementById("uiQosDown")
    div.innerHTML = allDivsStr("uiQosDown", True)
    div = document.getElementById("uiQosDownYScale")
    div.innerHTML = yScaleStr('uiQosDown')
    div = document.getElementById("uiQosUp")
    div.innerHTML = allDivsStr("uiQosUp", True)
    div = document.getElementById("uiQosUpYScale")
    div.innerHTML = yScaleStr('uiQosUp')

def change_time_interval_ajax(refresh_time):
    if (g_refresh_interval_object) window.clearInterval(g_refresh_interval_object)
    g_refresh_interval_object = window.setInterval(RefreshPageContent, refresh_time)

def RefreshPageContent(part):
    my_url = "/internet/inetstat_monitor.lua?sid=0180e27f30cd9047&useajax=1&action=get_table"
    sendUpdateRequest()

    def sendUpdateRequest():
        ajaxGet(my_url, cbUpdateTable)

    def cbUpdateTable(xhr):
        txt = xhr.responseText or "null"
        if (xhr.status != 200) {
            return
        }
        jxl.setHtml("uiInternetMonitor", txt)
        zebra()
        obj = document.getElementById("uiConnectState")
        if (obj and obj.value == "5") {
            jxl.enable("uiReconnectBtn")
        }

def uiDoRefresh():
    if (g_refresh_interval_object) {
        window.clearInterval(g_refresh_interval_object)
    }
    if (g_Timer) {
        window.clearTimeout(g_Timer)
    }
    location.href = ""

def connect_again():
    my_url = "/internet/inetstat_monitor.lua?sid=0180e27f30cd9047&useajax=1&action=connect"
    sendUpdateRequest()

    def sendUpdateRequest():
        ajaxGet(my_url, cbConnected)

    def cbConnected():
        jxl.enable("uiReconnectBtn")
        jxl.hide("uiWarnDisconnecting")
        RefreshPageContent()
        change_time_interval_ajax(g_refresh_time)

def DoDisconnectInternet():
    my_url = "/internet/inetstat_monitor.lua?sid=0180e27f30cd9047&useajax=1&action=disconnect"
    sendUpdateRequest()

    def sendUpdateRequest():
        change_time_interval_ajax(2000)
        jxl.disable("uiReconnectBtn")
        jxl.show("uiWarnDisconnecting")
        ajaxGet(my_url, cbDisconnected)

    def cbDisconnected():
        window.setTimeout("connect_again()", 6000)
        window.setTimeout(def ():
            change_time_interval_ajax(g_refresh_time)
    return False

                          def init():
    updateValues()
    if (g_refresh_interval_object) window.clearInterval(g_refresh_interval_object)
    RefreshPageContent()
    g_refresh_interval_object = window.setInterval(RefreshPageContent, g_refresh_time)
    window.setTimeout(uiDoRefresh, 60 * 60 * 1000)
ready.onReady(init)
