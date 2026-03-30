import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland
import QtQuick
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

PanelWindow {
    id: bar
    visible: true
    exclusionMode: ExclusionMode.Exclusive
    WlrLayershell.layer: WlrLayer.Top
    WlrLayershell.namespace: "quickshell"
    anchors { top: true; left: true; right: true }
    margins { top: 7; left: 7; right: 7 }
    implicitHeight: 40
    color: "transparent"

    property int barHeight: 40
    property int capRadius: 10
    property color barBg: Qt.rgba(0, 0, 0, 0.50)
    property color capBg: Qt.rgba(0, 0, 0, 0.35)

    property int activeWsId: 1
    property int targetWsId: 1
    property string mediaText: ""
    property string mediaClass: "stopped"
    property real mediaPosition: 0
    property real mediaLength: 0
    property string volumeStr: "󰕾 0%"
    property int volumePercent: 50
    property bool volumeMuted: false
    property bool wifiConnected: false
    property string wifiSSID: ""
    property int wifiStrength: 0
    property bool btConnected: false
    property var cavaValues: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    property bool volumeAdjusting: false
    property real pendingVolume: 0

    Connections {
        target: Hyprland
        function onRawEvent(event) {
            if (event.name === "workspace") {
                var wsId = parseInt(event.data.trim())
                if (!isNaN(wsId)) { bar.targetWsId = wsId; wsTransition.restart() }
            } else if (event.name === "focusedmon") {
                var parts = event.data.split(",")
                if (parts.length >= 2) {
                    var wsId = parseInt(parts[1])
                    if (!isNaN(wsId)) { bar.targetWsId = wsId; wsTransition.restart() }
                }
            }
        }
    }

    SequentialAnimation {
        id: wsTransition
        PropertyAnimation { target: wsHighlight; property: "highlightOpacity"; to: 0.4; duration: 50; easing.type: Easing.OutQuad }
        ScriptAction { script: bar.activeWsId = bar.targetWsId }
        ParallelAnimation {
            PropertyAnimation { target: wsHighlight; property: "highlightOpacity"; to: 1; duration: 300; easing.type: Easing.OutCubic }
            PropertyAnimation { target: wsHighlight; property: "highlightScale"; from: 0.9; to: 1.0; duration: 300; easing.type: Easing.OutBack; easing.overshoot: 1.5 }
        }
    }

    Component.onCompleted: {
        if (Hyprland.focusedMonitor && Hyprland.focusedMonitor.activeWorkspace) {
            bar.activeWsId = Hyprland.focusedMonitor.activeWorkspace.id
            bar.targetWsId = bar.activeWsId
        }
    }

    Timer { interval: 1500; running: true; repeat: true; triggeredOnStart: true; onTriggered: { if (!mediaProc.running) mediaProc.running = true } }

    Process {
        id: cavaProc
        running: bar.mediaClass === "playing"
        command: ["cava", "-p", Quickshell.env("HOME") + "/.config/cava/config_raw"]
        stdout: SplitParser {
            onRead: data => {
                var parts = data.trim().split(";")
                var vals = []
                for (var i = 0; i < 12 && i < parts.length; i++) vals.push(parseInt(parts[i]) / 255)
                while (vals.length < 12) vals.push(0.1)
                bar.cavaValues = vals
            }
        }
    }

    Timer { interval: 80; running: bar.mediaClass !== "playing"; repeat: true
        onTriggered: { var v = []; for (var i = 0; i < 12; i++) v.push(bar.cavaValues[i] * 0.85); bar.cavaValues = v }
    }

    Process {
        id: mediaProc
        command: ["bash", "-c", "status=$(playerctl --player=%any status 2>/dev/null); pos=$(playerctl --player=%any position 2>/dev/null | cut -d. -f1); len=$(playerctl --player=%any metadata mpris:length 2>/dev/null); len=$((len / 1000000)); if [ \"$status\" = \"Playing\" ] || [ \"$status\" = \"Paused\" ]; then artist=$(playerctl --player=%any metadata artist 2>/dev/null); title=$(playerctl --player=%any metadata title 2>/dev/null); if [ -n \"$title\" ]; then text=\"$title\"; [ -n \"$artist\" ] && text=\"$artist - $title\"; if [ ${#text} -gt 35 ]; then text=\"${text:0:32}...\"; fi; echo \"$status|$text|$pos|$len\"; else echo 'stopped||0|0'; fi; else echo 'stopped||0|0'; fi"]
        stdout: SplitParser {
            onRead: data => {
                var parts = data.trim().split("|")
                if (parts.length >= 4) {
                    bar.mediaClass = parts[0].toLowerCase()
                    bar.mediaText = parts[1]
                    bar.mediaPosition = parseInt(parts[2]) || 0
                    bar.mediaLength = parseInt(parts[3]) || 0
                }
            }
        }
    }

    Timer { interval: 1000; running: bar.mediaClass === "playing"; repeat: true
        onTriggered: { if (bar.mediaPosition < bar.mediaLength) bar.mediaPosition += 1 }
    }

    Timer { interval: 800; running: true; repeat: true; triggeredOnStart: true; onTriggered: { if (!volumeProc.running) volumeProc.running = true } }

    Process {
        id: volumeProc
        command: ["bash", "-c", "vol=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ 2>/dev/null); muted=$(echo \"$vol\" | grep -q MUTED && echo 1 || echo 0); pct=$(echo \"$vol\" | awk '{printf \"%.0f\", $2 * 100}'); echo \"$pct|$muted\""]
        stdout: SplitParser {
            onRead: data => {
                var parts = data.trim().split("|")
                bar.volumePercent = parseInt(parts[0]) || 0
                bar.volumeMuted = parts[1] === "1"
                if (bar.volumeMuted) { bar.volumeStr = "󰝟 mute" }
                else { var icon = bar.volumePercent > 50 ? "󰕾" : (bar.volumePercent > 0 ? "󰖀" : "󰕿"); bar.volumeStr = icon + " " + bar.volumePercent + "%" }
            }
        }
    }

    Timer { id: volumeDebounce; interval: 150; repeat: false
        onTriggered: { volumeSetProc.command = ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", bar.pendingVolume + "%"]; volumeSetProc.running = true }
    }
    Process { id: volumeSetProc; onExited: { bar.volumeAdjusting = false; if (!volumeProc.running) volumeProc.running = true } }

    function adjustVolume(delta) {
        bar.volumeAdjusting = true
        bar.pendingVolume = Math.max(0, Math.min(100, bar.volumePercent + delta))
        bar.volumePercent = bar.pendingVolume
        var icon = bar.volumePercent > 50 ? "󰕾" : (bar.volumePercent > 0 ? "󰖀" : "󰕿")
        bar.volumeStr = icon + " " + bar.volumePercent + "%"
        volumeDebounce.restart()
    }

    Timer { interval: 5000; running: true; repeat: true; triggeredOnStart: true; onTriggered: { if (!networkProc.running) networkProc.running = true } }

    Process {
        id: networkProc
        command: ["bash", "-c", "wifi=$(nmcli -t -f active,ssid,signal dev wifi 2>/dev/null | grep '^yes' | head -1); if [ -n \"$wifi\" ]; then ssid=$(echo \"$wifi\" | cut -d: -f2); sig=$(echo \"$wifi\" | cut -d: -f3); echo \"1|$ssid|$sig\"; else echo '0||0'; fi; bt='0'; devices=$(echo -e 'devices\\nquit' | bluetoothctl 2>/dev/null | grep '^Device' | awk '{print $2}'); for mac in $devices; do if echo -e \"info $mac\\nquit\" | bluetoothctl 2>/dev/null | grep -q 'Connected: yes'; then bt='1'; break; fi; done; echo \"bt:$bt\""]
        stdout: SplitParser {
            onRead: data => {
                var line = data.trim()
                if (line.startsWith("bt:")) { bar.btConnected = line.endsWith("1") }
                else {
                    var parts = line.split("|")
                    bar.wifiConnected = parts[0] === "1"
                    bar.wifiSSID = parts.length > 1 ? parts[1] : ""
                    bar.wifiStrength = parts.length > 2 ? parseInt(parts[2]) : 0
                }
            }
        }
    }

    Process { id: volumeToggleProc; command: ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"]; onExited: { if (!volumeProc.running) volumeProc.running = true } }
    Process { id: mediaPlayPauseProc; command: ["playerctl", "play-pause"]; onExited: { if (!mediaProc.running) mediaProc.running = true } }
    Process { id: mediaNextProc; command: ["playerctl", "next"]; onExited: { if (!mediaProc.running) mediaProc.running = true } }
    Process { id: mediaPrevProc; command: ["playerctl", "previous"]; onExited: { if (!mediaProc.running) mediaProc.running = true } }

    Item {
        anchors.fill: parent

        // Фон бара с закруглёнными углами
        Rectangle {
            anchors.fill: parent
            radius: bar.capRadius
            color: bar.barBg
        }

        // ===== ЛЕВАЯ ЧАСТЬ =====
        Row {
            anchors.left: parent.left
            anchors.leftMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6

            // Капсула: иконка + часы
            Rectangle {
                height: bar.barHeight - 10
                radius: bar.capRadius
                color: bar.capBg
                width: leftCapRow.width + 20
                anchors.verticalCenter: parent.verticalCenter

                Row {
                    id: leftCapRow
                    anchors.centerIn: parent
                    spacing: 8

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "󰣇"
                        color: root.walColor1
                        font.pixelSize: 15
                        font.family: "JetBrainsMono Nerd Font"
                    }

                    Rectangle { width: 1; height: 14; color: Qt.rgba(1,1,1,0.15); anchors.verticalCenter: parent.verticalCenter }

                    Text {
                        id: clockLabel
                        anchors.verticalCenter: parent.verticalCenter
                        text: Qt.formatDateTime(new Date(), "hh:mm AP")
                        color: root.walColor5
                        font.pixelSize: 11
                        font.bold: true
                        font.family: "JetBrainsMono Nerd Font"
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    onClicked: function(mouse) {
                        if (mouse.button === Qt.RightButton) {
                            root.activeTab = 1
                            if (!root.launcherVisible) root.toggleLauncher()
                            else { root.activeTab = 1; if (!root.wallsLoaded) root.loadWallpapers() }
                        } else {
                            root.activeTab = 0
                            root.toggleLauncher()
                        }
                    }
                }

                Timer { interval: 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: clockLabel.text = Qt.formatDateTime(new Date(), "hh:mm AP") }
            }

            // Капсула: воркспейсы
            Rectangle {
                height: bar.barHeight - 10
                radius: bar.capRadius
                color: bar.capBg
                width: wsContainer.width + 20
                anchors.verticalCenter: parent.verticalCenter
                Behavior on width { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }

                Item {
                    id: wsContainer
                    anchors.centerIn: parent
                    width: wsRow.width
                    height: 20

                    Rectangle {
                        id: wsHighlight
                        height: 20; radius: 10
                        property real targetX: 0
                        property real targetWidth: 26
                        property real highlightOpacity: 1.0
                        property real highlightScale: 1.0
                        x: targetX; width: targetWidth
                        opacity: highlightOpacity; scale: highlightScale
                        transformOrigin: Item.Center
                        color: root.walColor13
                        antialiasing: true
                        Behavior on x { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }
                        Behavior on width { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
                    }

                    Row {
                        id: wsRow
                        anchors.centerIn: parent
                        spacing: 4
                        Repeater {
                            id: wsRepeater
                            model: Hyprland.workspaces
                            delegate: Item {
                                id: wsDelegate
                                required property var modelData
                                property bool isActive: bar.activeWsId === modelData.id
                                visible: modelData.id > 0
                                width: Math.max(wsText.implicitWidth + 14, 26)
                                height: 20
                                onIsActiveChanged: updateHighlight()
                                onXChanged: if (isActive) updateHighlight()
                                onWidthChanged: if (isActive) updateHighlight()
                                Component.onCompleted: if (isActive) updateHighlight()
                                function updateHighlight() {
                                    if (isActive) { wsHighlight.targetX = x; wsHighlight.targetWidth = width }
                                }
                                Text {
                                    id: wsText
                                    anchors.centerIn: parent
                                    text: modelData.name || modelData.id.toString()
                                    color: isActive ? root.walBackground : Qt.rgba(root.walForeground.r, root.walForeground.g, root.walForeground.b, 0.5)
                                    font.pixelSize: 10; font.bold: true
                                    font.family: "JetBrainsMono Nerd Font"
                                    Behavior on color { ColorAnimation { duration: 200 } }
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: Hyprland.dispatch("workspace " + modelData.id)
                                }
                            }
                        }
                    }
                    Connections {
                        target: bar
                        function onActiveWsIdChanged() {
                            for (var i = 0; i < wsRepeater.count; i++) {
                                var item = wsRepeater.itemAt(i)
                                if (item && item.isActive) { item.updateHighlight(); break }
                            }
                        }
                    }
                }
            }
        }

        // ===== ЦЕНТР: медиа =====
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            height: bar.barHeight - 10
            radius: bar.capRadius
            color: bar.capBg
            visible: bar.mediaText !== ""
            width: visible ? mediaInner.width + 20 : 0
            Behavior on width { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }

            Row {
                id: mediaInner
                anchors.centerIn: parent
                spacing: 8

                Row {
                    spacing: 2
                    anchors.verticalCenter: parent.verticalCenter
                    Repeater {
                        model: 12
                        Rectangle {
                            width: 2.5
                            height: Math.max(3, bar.cavaValues[index] * 14)
                            radius: 1.25
                            anchors.verticalCenter: parent.verticalCenter
                            color: root.walColor5
                            antialiasing: true
                            Behavior on height { NumberAnimation { duration: 60; easing.type: Easing.OutQuad } }
                        }
                    }
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: bar.mediaText
                    color: root.walColor2
                    font.pixelSize: 11; font.bold: true
                    font.family: "JetBrainsMono Nerd Font"
                    opacity: bar.mediaClass === "playing" ? 1.0 : 0.6
                    Behavior on opacity { NumberAnimation { duration: 300 } }
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
                onClicked: function(mouse) {
                    if (mouse.button === Qt.RightButton) root.toggleMusic()
                    else if (mouse.button === Qt.MiddleButton) { if (!mediaNextProc.running) mediaNextProc.running = true }
                    else { if (!mediaPlayPauseProc.running) mediaPlayPauseProc.running = true }
                }
                onWheel: function(wheel) {
                    if (wheel.angleDelta.y > 0) { if (!mediaNextProc.running) mediaNextProc.running = true }
                    else { if (!mediaPrevProc.running) mediaPrevProc.running = true }
                }
            }
        }

        // ===== ПРАВАЯ ЧАСТЬ =====
        Row {
            anchors.right: parent.right
            anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6

            // Капсула: громкость
            Rectangle {
                height: bar.barHeight - 10
                radius: bar.capRadius
                color: bar.capBg
                width: volumeLabel.implicitWidth + 20
                anchors.verticalCenter: parent.verticalCenter

                Text {
                    id: volumeLabel
                    anchors.centerIn: parent
                    text: bar.volumeStr
                    color: bar.volumeMuted ? root.walColor8 : root.walColor5
                    font.pixelSize: 11; font.bold: true
                    font.family: "JetBrainsMono Nerd Font"
                    Behavior on color { ColorAnimation { duration: 200 } }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: { if (!volumeToggleProc.running) volumeToggleProc.running = true }
                    onWheel: function(wheel) { bar.adjustVolume(wheel.angleDelta.y > 0 ? 5 : -5) }
                }
            }

            // Капсула: сеть + BT
            Rectangle {
                height: bar.barHeight - 10
                radius: bar.capRadius
                color: bar.capBg
                width: netRow.width + 20
                anchors.verticalCenter: parent.verticalCenter

                Row {
                    id: netRow
                    anchors.centerIn: parent
                    spacing: 6

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: {
                            if (!bar.wifiConnected) return "󰤭"
                            if (bar.wifiStrength > 75) return "󰤨"
                            if (bar.wifiStrength > 50) return "󰤥"
                            if (bar.wifiStrength > 25) return "󰤢"
                            return "󰤟"
                        }
                        color: bar.wifiConnected ? root.walColor2 : root.walColor8
                        font.pixelSize: 14; font.family: "JetBrainsMono Nerd Font"
                        Behavior on color { ColorAnimation { duration: 300 } }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: bar.btConnected ? "󰂱" : "󰂲"
                        color: bar.btConnected ? root.walColor5 : root.walColor8
                        font.pixelSize: 13; font.family: "JetBrainsMono Nerd Font"
                        Behavior on color { ColorAnimation { duration: 300 } }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    onClicked: function(mouse) {
                        if (mouse.button === Qt.RightButton) root.toggleBluetooth()
                        else root.toggleWifi()
                    }
                }
            }

            // Капсула: дашборд
            Rectangle {
                height: bar.barHeight - 10
                width: height
                radius: bar.capRadius
                color: bar.capBg
                anchors.verticalCenter: parent.verticalCenter

                Text {
                    anchors.centerIn: parent
                    text: "󰕮"
                    color: root.walColor1
                    font.pixelSize: 15; font.family: "JetBrainsMono Nerd Font"
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.toggleDashboard()
                }
            }
        }
    }
}
