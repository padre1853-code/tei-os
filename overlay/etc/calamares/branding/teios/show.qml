/* Tei OS installer slideshow — every size is relative to the slide, so it fits any window size. */
import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    Timer {
        interval: 9000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    Slide {
        x: 0; y: 0; width: presentation.width; height: presentation.height
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#17656F" }
                GradientStop { position: 1.0; color: "#0B3A41" }
            }
        }
        Image {
            id: shot1
            source: "shot1.png"
            anchors.top: parent.top
            anchors.topMargin: parent.height * 0.05
            anchors.horizontalCenter: parent.horizontalCenter
            height: Math.min(parent.height * 0.56, parent.width * 0.9 * 384 / 664)
            width: height * 664 / 384
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
        Text {
            id: title1
            anchors.top: shot1.bottom
            anchors.topMargin: parent.height * 0.035
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.88
            text: "Bun venit în Tei OS"
            color: "#FFFFFF"
            font.pixelSize: Math.max(15, Math.min(24, parent.height * 0.055))
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
        Rectangle {
            id: bar1
            anchors.top: title1.bottom
            anchors.topMargin: parent.height * 0.02
            anchors.horizontalCenter: parent.horizontalCenter
            width: 70; height: 3; radius: 1
            color: "#F6B84E"
        }
        Text {
            anchors.top: bar1.bottom
            anchors.topMargin: parent.height * 0.025
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.84
            text: "Un desktop clasic și familiar: butonul Start, bara de activități și ferestrele cu care sunteți obișnuit. Rapid, sigur și gratuit."
            color: "#DDF0F2"
            font.pixelSize: Math.max(11, Math.min(15, parent.height * 0.036))
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }

    Slide {
        x: 0; y: 0; width: presentation.width; height: presentation.height
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#17656F" }
                GradientStop { position: 1.0; color: "#0B3A41" }
            }
        }
        Image {
            id: shot2
            source: "shot2.png"
            anchors.top: parent.top
            anchors.topMargin: parent.height * 0.05
            anchors.horizontalCenter: parent.horizontalCenter
            height: Math.min(parent.height * 0.56, parent.width * 0.9 * 384 / 664)
            width: height * 664 / 384
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
        Text {
            id: title2
            anchors.top: shot2.bottom
            anchors.topMargin: parent.height * 0.035
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.88
            text: "Toate setările, într-un singur loc"
            color: "#FFFFFF"
            font.pixelSize: Math.max(15, Math.min(24, parent.height * 0.055))
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
        Rectangle {
            id: bar2
            anchors.top: title2.bottom
            anchors.topMargin: parent.height * 0.02
            anchors.horizontalCenter: parent.horizontalCenter
            width: 70; height: 3; radius: 1
            color: "#F6B84E"
        }
        Text {
            anchors.top: bar2.bottom
            anchors.topMargin: parent.height * 0.025
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.84
            text: "Panoul de control grupează pe categorii rețeaua, imprimantele, utilizatorii, actualizările, data și ora — totul din interfața grafică."
            color: "#DDF0F2"
            font.pixelSize: Math.max(11, Math.min(15, parent.height * 0.036))
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }

    Slide {
        x: 0; y: 0; width: presentation.width; height: presentation.height
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#17656F" }
                GradientStop { position: 1.0; color: "#0B3A41" }
            }
        }
        Image {
            id: shot3
            source: "shot3.png"
            anchors.top: parent.top
            anchors.topMargin: parent.height * 0.05
            anchors.horizontalCenter: parent.horizontalCenter
            height: Math.min(parent.height * 0.56, parent.width * 0.9 * 384 / 664)
            width: height * 664 / 384
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
        Text {
            id: title3
            anchors.top: shot3.bottom
            anchors.topMargin: parent.height * 0.035
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.88
            text: "Programele de zi cu zi sunt incluse"
            color: "#FFFFFF"
            font.pixelSize: Math.max(15, Math.min(24, parent.height * 0.055))
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
        Rectangle {
            id: bar3
            anchors.top: title3.bottom
            anchors.topMargin: parent.height * 0.02
            anchors.horizontalCenter: parent.horizontalCenter
            width: 70; height: 3; radius: 1
            color: "#F6B84E"
        }
        Text {
            anchors.top: bar3.bottom
            anchors.topMargin: parent.height * 0.025
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.84
            text: "Navigator web, LibreOffice compatibil cu documentele Word, Excel și PowerPoint, cititor PDF, player video și desktop la distanță."
            color: "#DDF0F2"
            font.pixelSize: Math.max(11, Math.min(15, parent.height * 0.036))
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }

    Slide {
        x: 0; y: 0; width: presentation.width; height: presentation.height
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#17656F" }
                GradientStop { position: 1.0; color: "#0B3A41" }
            }
        }
        Image {
            id: shot4
            source: "shot4.png"
            anchors.top: parent.top
            anchors.topMargin: parent.height * 0.05
            anchors.horizontalCenter: parent.horizontalCenter
            height: Math.min(parent.height * 0.56, parent.width * 0.9 * 384 / 664)
            width: height * 664 / 384
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
        Text {
            id: title4
            anchors.top: shot4.bottom
            anchors.topMargin: parent.height * 0.035
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.88
            text: "Pregătit pentru rețeaua firmei"
            color: "#FFFFFF"
            font.pixelSize: Math.max(15, Math.min(24, parent.height * 0.055))
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
        Rectangle {
            id: bar4
            anchors.top: title4.bottom
            anchors.topMargin: parent.height * 0.02
            anchors.horizontalCenter: parent.horizontalCenter
            width: 70; height: 3; radius: 1
            color: "#F6B84E"
        }
        Text {
            anchors.top: bar4.bottom
            anchors.topMargin: parent.height * 0.025
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.84
            text: "Alăturare la domeniu Active Directory din Proprietăți sistem, partajări de rețea Windows și programe .exe pornite prin Wine."
            color: "#DDF0F2"
            font.pixelSize: Math.max(11, Math.min(15, parent.height * 0.036))
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }

    Slide {
        x: 0; y: 0; width: presentation.width; height: presentation.height
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#17656F" }
                GradientStop { position: 1.0; color: "#0B3A41" }
            }
        }
        Image {
            id: shot5
            source: "shot5.png"
            anchors.top: parent.top
            anchors.topMargin: parent.height * 0.05
            anchors.horizontalCenter: parent.horizontalCenter
            height: Math.min(parent.height * 0.56, parent.width * 0.9 * 384 / 664)
            width: height * 664 / 384
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
        Text {
            id: title5
            anchors.top: shot5.bottom
            anchors.topMargin: parent.height * 0.035
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.88
            text: "Aproape gata"
            color: "#FFFFFF"
            font.pixelSize: Math.max(15, Math.min(24, parent.height * 0.055))
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
        Rectangle {
            id: bar5
            anchors.top: title5.bottom
            anchors.topMargin: parent.height * 0.02
            anchors.horizontalCenter: parent.horizontalCenter
            width: 70; height: 3; radius: 1
            color: "#F6B84E"
        }
        Text {
            anchors.top: bar5.bottom
            anchors.topMargin: parent.height * 0.025
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.84
            text: "După repornire, scoateți mediul de instalare. Fereastra Bun venit vă ajută cu actualizările, driverele și restaurarea sistemului."
            color: "#DDF0F2"
            font.pixelSize: Math.max(11, Math.min(15, parent.height * 0.036))
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }
}
