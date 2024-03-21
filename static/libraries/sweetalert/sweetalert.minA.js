!function (e, t, n) {
    "use strict";
    !function o(e, t, n) {
        function a(s, l) {
            if (!t[s]) {
                if (!e[s]) {
                    var i = "function" == typeof require && require;
                    if (!l && i)
                        return i(s, !0);
                    if (r)
                        return r(s, !0);
                    var u = new Error("Cannot find module '" + s + "'");
                    throw u.code = "MODULE_NOT_FOUND", u
                }
                var c = t[s] = {
                    exports: {}
                };
                e[s][0].call(c.exports, function (t) {
                    var n = e[s][1][t];
                    return a(n ? n : t)
                }, c, c.exports, o, e, t, n)
            }
            return t[s].exports
        }
        for (var r = "function" == typeof require && require, s = 0; s < n.length; s++)
            a(n[s]);
        return a
    }({
        1: [function (o, a, r) {
                var s = function (e) {
                    return e && e.__esModule ? e : {
                        "default": e
                    }
                };
                Object.defineProperty(r, "__esModule", {
                    value: !0
                });
                var l, i, u, c, d = o("./modules/handle-dom"),
                        f = o("./modules/utils"),
                        p = o("./modules/handle-swal-dom"),
                        m = o("./modules/handle-click"),
                        v = o("./modules/handle-key"),
                        y = s(v),
                        h = o("./modules/default-params"),
                        b = s(h),
                        g = o("./modules/set-params"),
                        w = s(g);
                r["default"] = u = c = function () {
                    function o(e) {
                        var t = a;
                        return t[e] === n ? b["default"][e] : t[e]
                    }
                    var a = arguments[0];
                    if (d.addClass(t.body, "stop-scrolling"), p.resetInput(), a === n)
                        return f.logStr("SweetAlert expects at least 1 attribute!"), !1;
                    var r = f.extend({}, b["default"]);
                    switch (typeof a) {
                        case "string":
                            r.title = a, r.text = arguments[1] || "", r.type = arguments[2] || "";
                            break;
                        case "object":
                            if (a.title === n)
                                return f.logStr('Missing "title" argument!'), !1;
                            r.title = a.title;
                            for (var s in b["default"])
                                r[s] = o(s);
                            r.confirmButtonText = r.showCancelButton ? "Confirm" : b["default"].confirmButtonText, r.confirmButtonText = o("confirmButtonText"), r.doneFunction = arguments[1] || null;
                            break;
                        default:
                            return f.logStr('Unexpected type of argument! Expected "string" or "object", got ' + typeof a), !1
                    }
                    w["default"](r), p.fixVerticalPosition(), p.openModal(arguments[1]);
                    for (var u = p.getModal(), v = u.querySelectorAll("button"), h = ["onclick", "onmouseover", "onmouseout", "onmousedown", "onmouseup", "onfocus"], g = function (e) {
                        return m.handleButton(e, r, u)
                    }, C = 0; C < v.length; C++)
                        for (var S = 0; S < h.length; S++) {
                            var x = h[S];
                            v[C][x] = g
                        }
                    p.getOverlay().onclick = g, l = e.onkeydown;
                    var k = function (e) {
                        return y["default"](e, r, u)
                    };
                    e.onkeydown = k, e.onfocus = function () {
                        setTimeout(function () {
                            i !== n && (i.focus(), i = n)
                        }, 0)
                    }, c.enableButtons()
                }, u.setDefaults = c.setDefaults = function (e) {
                    if (!e)
                        throw new Error("userParams is required");
                    if ("object" != typeof e)
                        throw new Error("userParams has to be a object");
                    f.extend(b["default"], e)
                }, u.close = c.close = function () {
                    var o = p.getModal();
                    /* 
                     * @author David Pérez Negrete
                     * @targetdocument ALL JSP
                     * @version 0.1, 05/10/16
                     * @description funcion para determinar los 'hide' de modals 
                     */

                    var jsp = document.getElementById('jsp').value;
                    if (jsp == 'Equivalencia') {
                        AccionesModalsEquivalenciaJSP();
                    } else if (jsp == 'Administrativo') {
                        AccionesModalsAdministrativoJSP();
                    } else if (jsp == 'Avisos') {
                        AccionesModalsAvisoJSP();
                    } else if (jsp == 'Eventos') {
                        AccionesModalsCalendarioJSP();
                    } else if (jsp == 'PerfilInstitucional') {
                        AccionesModalsPerfilInstitucionalJSP();
                    } else if (jsp == 'ParamCalif') {
                        AccionesModalsParamCalifJSP();
                    } else if (jsp == 'CicloEscolar') {
                        AccionesModalsCicloEscJSP();
                    } else if (jsp == 'Incorporaciones') {
                        AccionesModalsIncorporacionesJSP();
                    } else if (jsp == 'Alumno') {
                        AccionesModalsAlumnosJSP();
                    } else if (jsp == 'ExAlumno') {
                        AccionesModalsExAlumnosJSP();
                    } else if (jsp == 'FamAlumno') {
                        AccionesModalsFamAlumnosJSP();
                    } else if (jsp == 'PeriodosCalificacion') {
                        AccionesModalsPeriodoCalJSP();
                    } else if (jsp == 'Generacion') {
                        AccionesModalsGeneracionJSP();
                    } else if (jsp == 'Grupo') {
                        AccionesModalsGrupoJSP();
                    } else if (jsp == 'Aviso') {
                        AccionesModalsAvisoJSP();
                    } else if (jsp == 'Docente') {
                        AccionesModalsDocenteJSP();
                    } else if (jsp == 'Usuario') {
                        AccionesModalsUsuarioJSP();
                    } else if (jsp == 'Rol') {
                        AccionesModalsRolJSP();
                    } else if (jsp == 'HoraDia') {
                        AccionesModalsHoraDiaJSP();

                    } else if (jsp == 'EstAcademica') {
                        AccionesModalsEstAcademicaJSP();
                    } else if (jsp === 'Page500') {
                        AccionesPageError();
                    } else if (jsp === 'Page404') {
                        AccionesPageError();
                    } else if (jsp === 'AvisoAlumno') {
                        CerrarModalMensajeSoporte();
                    } else if (jsp === 'InicioAlumno') {
                        CerrarModalMensajeSoporte();
                    } else if (jsp === 'InicioDocente') {
                        CerrarModalMensajeSoporte();
                    } else if (jsp === 'InicioFamiliar') {
                        CerrarModalMensajeSoporte();
                    } else if (jsp === 'inboxControlEscolar') {
                        AccionesImboxControlEscolar();
                    } else if (jsp == 'PerfilAlumno') {
                        AccionesPerfilAlumnoJSP();
                    } else if (jsp == 'TareaAlumno') {
                        AccionesTareaAlumno();
                    }



                    d.fadeOut(p.getOverlay(), 5), d.fadeOut(o, 5), d.removeClass(o, "showSweetAlert"), d.addClass(o, "hideSweetAlert"), d.removeClass(o, "visible");
                    var a = o.querySelector(".sa-icon.sa-success");
                    d.removeClass(a, "animate"), d.removeClass(a.querySelector(".sa-tip"), "animateSuccessTip"), d.removeClass(a.querySelector(".sa-long"), "animateSuccessLong");
                    var r = o.querySelector(".sa-icon.sa-error");
                    d.removeClass(r, "animateErrorIcon"), d.removeClass(r.querySelector(".sa-x-mark"), "animateXMark");
                    var s = o.querySelector(".sa-icon.sa-warning");
                    return d.removeClass(s, "pulseWarning"), d.removeClass(s.querySelector(".sa-body"), "pulseWarningIns"), d.removeClass(s.querySelector(".sa-dot"), "pulseWarningIns"), setTimeout(function () {
                        var e = o.getAttribute("data-custom-class");
                        d.removeClass(o, e)
                    }, 300), d.removeClass(t.body, "stop-scrolling"), e.onkeydown = l, e.previousActiveElement && e.previousActiveElement.focus(), i = n, clearTimeout(o.timeout), !0
                }, u.showInputError = c.showInputError = function (e) {
                    var t = p.getModal(),
                            n = t.querySelector(".sa-input-error");
                    d.addClass(n, "show");
                    var o = t.querySelector(".sa-error-container");
                    d.addClass(o, "show"), o.querySelector("p").innerHTML = e, setTimeout(function () {
                        u.enableButtons()
                    }, 1), t.querySelector("input").focus()
                }, u.resetInputError = c.resetInputError = function (e) {
                    if (e && 13 === e.keyCode)
                        return !1;
                    var t = p.getModal(),
                            n = t.querySelector(".sa-input-error");
                    d.removeClass(n, "show");
                    var o = t.querySelector(".sa-error-container");
                    d.removeClass(o, "show")
                }, u.disableButtons = c.disableButtons = function () {
                    var e = p.getModal(),
                            t = e.querySelector("button.confirm"),
                            n = e.querySelector("button.cancel");
                    t.disabled = !0, n.disabled = !0
                }, u.enableButtons = c.enableButtons = function () {
                    var e = p.getModal(),
                            t = e.querySelector("button.confirm"),
                            n = e.querySelector("button.cancel");
                    t.disabled = !1, n.disabled = !1
                }, "undefined" != typeof e ? e.sweetAlert = e.swal = u : f.logStr("SweetAlert is a frontend module!"), a.exports = r["default"]
            }, {
                "./modules/default-params": 2,
                "./modules/handle-click": 3,
                "./modules/handle-dom": 4,
                "./modules/handle-key": 5,
                "./modules/handle-swal-dom": 6,
                "./modules/set-params": 8,
                "./modules/utils": 9
            }],
        2: [function (e, t, n) {
                Object.defineProperty(n, "__esModule", {
                    value: !0
                });
                var o = {
                    title: "",
                    text: "",
                    type: null,
                    allowOutsideClick: !1,
                    showConfirmButton: !0,
                    showCancelButton: !1,
                    closeOnConfirm: !0,
                    closeOnCancel: !0,
                    confirmButtonText: "OK",
                    confirmButtonColor: "#8CD4F5",
                    cancelButtonText: "Cancelar",
                    imageUrl: null,
                    imageSize: null,
                    timer: null,
                    customClass: "",
                    html: !1,
                    animation: !0,
                    allowEscapeKey: !0,
                    inputType: "text",
                    inputPlaceholder: "",
                    inputValue: "",
                    showLoaderOnConfirm: !1
                };
                n["default"] = o, t.exports = n["default"]
            }, {}],
        3: [function (t, n, o) {
                Object.defineProperty(o, "__esModule", {
                    value: !0
                });
                var a = t("./utils"),
                        r = (t("./handle-swal-dom"), t("./handle-dom")),
                        s = function (t, n, o) {
                            function s(e) {
                                m && n.confirmButtonColor && (p.style.backgroundColor = e)
                            }
                            var u, c, d, f = t || e.event,
                                    p = f.target || f.srcElement,
                                    m = -1 !== p.className.indexOf("confirm"),
                                    v = -1 !== p.className.indexOf("sweet-overlay"),
                                    y = r.hasClass(o, "visible"),
                                    h = n.doneFunction && "true" === o.getAttribute("data-has-done-function");
                            switch (m && n.confirmButtonColor && (u = n.confirmButtonColor, c = a.colorLuminance(u, -.04), d = a.colorLuminance(u, -.14)), f.type) {
                                case "mouseover":
                                    s(c);
                                    break;
                                case "mouseout":
                                    s(u);
                                    break;
                                case "mousedown":
                                    s(d);
                                    break;
                                case "mouseup":
                                    s(c);
                                    break;
                                case "focus":
                                    var b = o.querySelector("button.confirm"),
                                            g = o.querySelector("button.cancel");
                                    m ? g.style.boxShadow = "none" : b.style.boxShadow = "none";
                                    break;
                                case "click":
                                    var w = o === p,
                                            C = r.isDescendant(o, p);
                                    if (!w && !C && y && !n.allowOutsideClick)
                                        break;
                                    m && h && y ? l(o, n) : h && y || v ? i(o, n) : r.isDescendant(o, p) && "BUTTON" === p.tagName && sweetAlert.close()
                            }
                        },
                        l = function (e, t) {
                            var n = !0;
                            r.hasClass(e, "show-input") && (n = e.querySelector("input").value, n || (n = "")), t.doneFunction(n), t.closeOnConfirm && sweetAlert.close(), t.showLoaderOnConfirm && sweetAlert.disableButtons()
                        },
                        i = function (e, t) {
                            var n = String(t.doneFunction).replace(/\s/g, ""),
                                    o = "function(" === n.substring(0, 9) && ")" !== n.substring(9, 10);
                            o && t.doneFunction(!1), t.closeOnCancel && sweetAlert.close()
                        };
                o["default"] = {
                    handleButton: s,
                    handleConfirm: l,
                    handleCancel: i
                }, n.exports = o["default"]
            }, {
                "./handle-dom": 4,
                "./handle-swal-dom": 6,
                "./utils": 9
            }],
        4: [function (n, o, a) {
                Object.defineProperty(a, "__esModule", {
                    value: !0
                });
                var r = function (e, t) {
                    return new RegExp(" " + t + " ").test(" " + e.className + " ")
                },
                        s = function (e, t) {
                            r(e, t) || (e.className += " " + t)
                        },
                        l = function (e, t) {
                            var n = " " + e.className.replace(/[\t\r\n]/g, " ") + " ";
                            if (r(e, t)) {
                                for (; n.indexOf(" " + t + " ") >= 0; )
                                    n = n.replace(" " + t + " ", " ");
                                e.className = n.replace(/^\s+|\s+$/g, "")
                            }
                        },
                        i = function (e) {
                            var n = t.createElement("div");
                            return n.appendChild(t.createTextNode(e)), n.innerHTML
                        },
                        u = function (e) {
                            e.style.opacity = "", e.style.display = "block"
                        },
                        c = function (e) {
                            if (e && !e.length)
                                return u(e);
                            for (var t = 0; t < e.length; ++t)
                                u(e[t])
                        },
                        d = function (e) {
                            e.style.opacity = "", e.style.display = "none"
                        },
                        f = function (e) {
                            if (e && !e.length)
                                return d(e);
                            for (var t = 0; t < e.length; ++t)
                                d(e[t])
                        },
                        p = function (e, t) {
                            for (var n = t.parentNode; null !== n; ) {
                                if (n === e)
                                    return !0;
                                n = n.parentNode
                            }
                            return !1
                        },
                        m = function (e) {
                            e.style.left = "-9999px", e.style.display = "block";
                            var t, n = e.clientHeight;
                            return t = "undefined" != typeof getComputedStyle ? parseInt(getComputedStyle(e).getPropertyValue("padding-top"), 10) : parseInt(e.currentStyle.padding), e.style.left = "", e.style.display = "none", "-" + parseInt((n + t) / 2) + "px"
                        },
                        v = function (e, t) {
                            if (+e.style.opacity < 1) {
                                t = t || 16, e.style.opacity = 0, e.style.display = "block";
                                var n = +new Date,
                                        o = function (e) {
                                            function t() {
                                                return e.apply(this, arguments)
                                            }
                                            return t.toString = function () {
                                                return e.toString()
                                            }, t
                                        }(function () {
                                    e.style.opacity = +e.style.opacity + (new Date - n) / 100, n = +new Date, +e.style.opacity < 1 && setTimeout(o, t)
                                });
                                o()
                            }
                            e.style.display = "block"
                        },
                        y = function (e, t) {
                            t = t || 16, e.style.opacity = 1;
                            var n = +new Date,
                                    o = function (e) {
                                        function t() {
                                            return e.apply(this, arguments)
                                        }
                                        return t.toString = function () {
                                            return e.toString()
                                        }, t
                                    }(function () {
                                e.style.opacity = +e.style.opacity - (new Date - n) / 100, n = +new Date, +e.style.opacity > 0 ? setTimeout(o, t) : e.style.display = "none"
                            });
                            o()
                        },
                        h = function (n) {
                            if ("function" == typeof MouseEvent) {
                                var o = new MouseEvent("click", {
                                    view: e,
                                    bubbles: !1,
                                    cancelable: !0
                                });
                                n.dispatchEvent(o)
                            } else if (t.createEvent) {
                                var a = t.createEvent("MouseEvents");
                                a.initEvent("click", !1, !1), n.dispatchEvent(a)
                            } else
                                t.createEventObject ? n.fireEvent("onclick") : "function" == typeof n.onclick && n.onclick()
                        },
                        b = function (t) {
                            "function" == typeof t.stopPropagation ? (t.stopPropagation(), t.preventDefault()) : e.event && e.event.hasOwnProperty("cancelBubble") && (e.event.cancelBubble = !0)
                        };
                a.hasClass = r, a.addClass = s, a.removeClass = l, a.escapeHtml = i, a._show = u, a.show = c, a._hide = d, a.hide = f, a.isDescendant = p, a.getTopMargin = m, a.fadeIn = v, a.fadeOut = y, a.fireClick = h, a.stopEventPropagation = b
            }, {}],
        5: [function (t, o, a) {
                Object.defineProperty(a, "__esModule", {
                    value: !0
                });
                var r = t("./handle-dom"),
                        s = t("./handle-swal-dom"),
                        l = function (t, o, a) {
                            var l = t || e.event,
                                    i = l.keyCode || l.which,
                                    u = a.querySelector("button.confirm"),
                                    c = a.querySelector("button.cancel"),
                                    d = a.querySelectorAll("button[tabindex]");
                            if (-1 !== [9, 13, 32, 27].indexOf(i)) {
                                for (var f = l.target || l.srcElement, p = -1, m = 0; m < d.length; m++)
                                    if (f === d[m]) {
                                        p = m;
                                        break
                                    }
                                9 === i ? (f = -1 === p ? u : p === d.length - 1 ? d[0] : d[p + 1], r.stopEventPropagation(l), f.focus(), o.confirmButtonColor && s.setFocusStyle(f, o.confirmButtonColor)) : 13 === i ? ("INPUT" === f.tagName && (f = u, u.focus()), f = -1 === p ? u : n) : 27 === i && o.allowEscapeKey === !0 ? (f = c, r.fireClick(f, l)) : f = n
                            }
                        };
                a["default"] = l, o.exports = a["default"]
            }, {
                "./handle-dom": 4,
                "./handle-swal-dom": 6
            }],
        6: [function (n, o, a) {
                var r = function (e) {
                    return e && e.__esModule ? e : {
                        "default": e
                    }
                };
                Object.defineProperty(a, "__esModule", {
                    value: !0
                });
                var s = n("./utils"),
                        l = n("./handle-dom"),
                        i = n("./default-params"),
                        u = r(i),
                        c = n("./injected-html"),
                        d = r(c),
                        f = ".sweet-alert",
                        p = ".sweet-overlay",
                        m = function () {
                            var e = t.createElement("div");
                            for (e.innerHTML = d["default"]; e.firstChild; )
                                t.body.appendChild(e.firstChild)
                        },
                        v = function (e) {
                            function t() {
                                return e.apply(this, arguments)
                            }
                            return t.toString = function () {
                                return e.toString()
                            }, t
                        }(function () {
                    var e = t.querySelector(f);
                    return e || (m(), e = v()), e
                }),
                        y = function () {
                            var e = v();
                            return e ? e.querySelector("input") : void 0
                        },
                        h = function () {
                            return t.querySelector(p)
                        },
                        b = function (e, t) {
                            var n = s.hexToRgb(t);
                            e.style.boxShadow = "0 0 2px rgba(" + n + ", 0.8), inset 0 0 0 1px rgba(0, 0, 0, 0.05)"
                        },
                        g = function (n) {
                            var o = v();
                            l.fadeIn(h(), 10), l.show(o), l.addClass(o, "showSweetAlert"), l.removeClass(o, "hideSweetAlert"), e.previousActiveElement = t.activeElement;
                            var a = o.querySelector("button.confirm");
                            a.focus(), setTimeout(function () {
                                l.addClass(o, "visible")
                            }, 500);
                            var r = o.getAttribute("data-timer");
                            if ("null" !== r && "" !== r) {
                                var s = n;
                                o.timeout = setTimeout(function () {
                                    var e = (s || null) && "true" === o.getAttribute("data-has-done-function");
                                    e ? s(null) : sweetAlert.close()
                                }, r)
                            }
                        },
                        w = function () {
                            var e = v(),
                                    t = y();
                            l.removeClass(e, "show-input"), t.value = u["default"].inputValue, t.setAttribute("type", u["default"].inputType), t.setAttribute("placeholder", u["default"].inputPlaceholder), C()
                        },
                        C = function (e) {
                            if (e && 13 === e.keyCode)
                                return !1;
                            var t = v(),
                                    n = t.querySelector(".sa-input-error");
                            l.removeClass(n, "show");
                            var o = t.querySelector(".sa-error-container");
                            l.removeClass(o, "show")
                        },
                        S = function () {
                            var e = v();
                            e.style.marginTop = l.getTopMargin(v())
                        };
                a.sweetAlertInitialize = m, a.getModal = v, a.getOverlay = h, a.getInput = y, a.setFocusStyle = b, a.openModal = g, a.resetInput = w, a.resetInputError = C, a.fixVerticalPosition = S
            }, {
                "./default-params": 2,
                "./handle-dom": 4,
                "./injected-html": 7,
                "./utils": 9
            }],
        7: [function (e, t, n) {
                Object.defineProperty(n, "__esModule", {
                    value: !0
                });
                var o = '<div class="sweet-overlay" tabIndex="-1"></div><div class="sweet-alert"><div class="sa-icon sa-error">\n      <span class="sa-x-mark">\n        <span class="sa-line sa-left"></span>\n        <span class="sa-line sa-right"></span>\n      </span>\n    </div><div class="sa-icon sa-warning">\n      <span class="sa-body"></span>\n      <span class="sa-dot"></span>\n    </div><div class="sa-icon sa-info"></div><div class="sa-icon sa-success">\n      <span class="sa-line sa-tip"></span>\n      <span class="sa-line sa-long"></span>\n\n      <div class="sa-placeholder"></div>\n      <div class="sa-fix"></div>\n    </div><div class="sa-icon sa-custom"></div><h2>Title</h2>\n    <p>Text</p>\n    <fieldset>\n      <input type="text" tabIndex="3" />\n      <div class="sa-input-error"></div>\n    </fieldset><div class="sa-error-container">\n      <div class="icon">!</div>\n      <p>Not valid!</p>\n    </div><div class="sa-button-container">\n      <button class="cancel" tabIndex="2">Cancel</button>\n      <div class="sa-confirm-button-container">\n        <button class="confirm" tabIndex="1">OK</button><div class="la-ball-fall">\n          <div></div>\n          <div></div>\n          <div></div>\n        </div>\n      </div>\n    </div></div>';
                n["default"] = o, t.exports = n["default"]
            }, {}],
        8: [function (e, t, o) {
                Object.defineProperty(o, "__esModule", {
                    value: !0
                });
                var a = e("./utils"),
                        r = e("./handle-swal-dom"),
                        s = e("./handle-dom"),
                        l = ["error", "warning", "info", "success", "input", "prompt"],
                        i = function (e) {
                            var t = r.getModal(),
                                    o = t.querySelector("h2"),
                                    i = t.querySelector("p"),
                                    u = t.querySelector("button.cancel"),
                                    c = t.querySelector("button.confirm");
                            if (o.innerHTML = e.html ? e.title : s.escapeHtml(e.title).split("\n").join("<br>"), i.innerHTML = e.html ? e.text : s.escapeHtml(e.text || "").split("\n").join("<br>"), e.text && s.show(i), e.customClass)
                                s.addClass(t, e.customClass), t.setAttribute("data-custom-class", e.customClass);
                            else {
                                var d = t.getAttribute("data-custom-class");
                                s.removeClass(t, d), t.setAttribute("data-custom-class", "")
                            }
                            if (s.hide(t.querySelectorAll(".sa-icon")), e.type && !a.isIE8()) {
                                var f = function () {
                                    for (var o = !1, a = 0; a < l.length; a++)
                                        if (e.type === l[a]) {
                                            o = !0;
                                            break
                                        }
                                    if (!o)
                                        return logStr("Unknown alert type: " + e.type), {
                                            v: !1
                                        };
                                    var i = ["success", "error", "warning", "info"],
                                            u = n;
                                    -1 !== i.indexOf(e.type) && (u = t.querySelector(".sa-icon.sa-" + e.type), s.show(u));
                                    var c = r.getInput();
                                    switch (e.type) {
                                        case "success":
                                            s.addClass(u, "animate"), s.addClass(u.querySelector(".sa-tip"), "animateSuccessTip"), s.addClass(u.querySelector(".sa-long"), "animateSuccessLong");
                                            break;
                                        case "error":
                                            s.addClass(u, "animateErrorIcon"), s.addClass(u.querySelector(".sa-x-mark"), "animateXMark");
                                            break;
                                        case "warning":
                                            s.addClass(u, "pulseWarning"), s.addClass(u.querySelector(".sa-body"), "pulseWarningIns"), s.addClass(u.querySelector(".sa-dot"), "pulseWarningIns");
                                            break;
                                        case "input":
                                        case "prompt":
                                            c.setAttribute("type", e.inputType), c.value = e.inputValue, c.setAttribute("placeholder", e.inputPlaceholder), s.addClass(t, "show-input"), setTimeout(function () {
                                                c.focus(), c.addEventListener("keyup", swal.resetInputError)
                                            }, 400)
                                    }
                                }();
                                if ("object" == typeof f)
                                    return f.v
                            }
                            if (e.imageUrl) {
                                var p = t.querySelector(".sa-icon.sa-custom");
                                p.style.backgroundImage = "url(" + e.imageUrl + ")", s.show(p);
                                var m = 80,
                                        v = 80;
                                if (e.imageSize) {
                                    var y = e.imageSize.toString().split("x"),
                                            h = y[0],
                                            b = y[1];
                                    h && b ? (m = h, v = b) : logStr("Parameter imageSize expects value with format WIDTHxHEIGHT, got " + e.imageSize)
                                }
                                p.setAttribute("style", p.getAttribute("style") + "width:" + m + "px; height:" + v + "px")
                            }
                            t.setAttribute("data-has-cancel-button", e.showCancelButton), e.showCancelButton ? u.style.display = "inline-block" : s.hide(u), t.setAttribute("data-has-confirm-button", e.showConfirmButton), e.showConfirmButton ? c.style.display = "inline-block" : s.hide(c), e.cancelButtonText && (u.innerHTML = s.escapeHtml(e.cancelButtonText)), e.confirmButtonText && (c.innerHTML = s.escapeHtml(e.confirmButtonText)), e.confirmButtonColor && (c.style.backgroundColor = e.confirmButtonColor, c.style.borderLeftColor = e.confirmLoadingButtonColor, c.style.borderRightColor = e.confirmLoadingButtonColor, r.setFocusStyle(c, e.confirmButtonColor)), t.setAttribute("data-allow-outside-click", e.allowOutsideClick);
                            var g = e.doneFunction ? !0 : !1;
                            t.setAttribute("data-has-done-function", g), e.animation ? "string" == typeof e.animation ? t.setAttribute("data-animation", e.animation) : t.setAttribute("data-animation", "pop") : t.setAttribute("data-animation", "none"), t.setAttribute("data-timer", e.timer)
                        };
                o["default"] = i, t.exports = o["default"]
            }, {
                "./handle-dom": 4,
                "./handle-swal-dom": 6,
                "./utils": 9
            }],
        9: [function (t, n, o) {
                Object.defineProperty(o, "__esModule", {
                    value: !0
                });
                var a = function (e, t) {
                    for (var n in t)
                        t.hasOwnProperty(n) && (e[n] = t[n]);
                    return e
                },
                        r = function (e) {
                            var t = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(e);
                            return t ? parseInt(t[1], 16) + ", " + parseInt(t[2], 16) + ", " + parseInt(t[3], 16) : null
                        },
                        s = function () {
                            return e.attachEvent && !e.addEventListener
                        },
                        l = function (t) {
                            e.console && e.console.log("SweetAlert: " + t)
                        },
                        i = function (e, t) {
                            e = String(e).replace(/[^0-9a-f]/gi, ""), e.length < 6 && (e = e[0] + e[0] + e[1] + e[1] + e[2] + e[2]), t = t || 0;
                            var n, o, a = "#";
                            for (o = 0; 3 > o; o++)
                                n = parseInt(e.substr(2 * o, 2), 16), n = Math.round(Math.min(Math.max(0, n + n * t), 255)).toString(16), a += ("00" + n).substr(n.length);
                            return a
                        };
                o.extend = a, o.hexToRgb = r, o.isIE8 = s, o.logStr = l, o.colorLuminance = i
            }, {}]
    }, {}, [1]), "function" == typeof define && define.amd ? define(function () {
        return sweetAlert
    }) : "undefined" != typeof module && module.exports && (module.exports = sweetAlert)
}(window, document);



/* Funciones para Jsp Equivalencia */
function CerrarModalMensajeSoporte() {
    $('#modal-mensajeReporte').modal('hide');
}

function CerrarModalCatEquivalencia() {
    var validator = $("form[name='FormCatalogoE']").validate();
    validator.resetForm();
    //$('#modal-Catequivalencia').modal('hide');
}

function CerrarModalParamCalificaciones() {
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-parametros-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#BtnNuevoparametros").attr('disabled', false);
    $('#modal-parametros').addClass("fade");
    $('#modal-parametros').attr('style', "display: none;");
    $('.mymodal').attr('style', '');


    $("#txtClave").val('').attr('disabled', false);
    $("#DivClave").removeClass('open');
    $("#txtDescParCal").val('').attr('disabled', false);
    $("#DivDescParCal").removeClass('open');
    $("#txtCMinimaParCal").val('').attr('disabled', false);
    $("#DivCMinimaParCal").removeClass('open');
    $("#txtNAsistenciaParCal").val('').attr('disabled', false);
    $("#DivNAsistenciaParCal").removeClass('open');
    $("#txtNDecimalParCal").val('').attr('disabled', false);
    $("#DivNDecimalParCal").removeClass('open');
    $("#txtaFormulaPar").val('').attr('disabled', false);
    $("#btnAddtoTable").attr('disabled', false);
    $("#txtClaveParCal").attr('disabled', false);


    $('#ChckEscalarCalificacion').prop('checked', true).attr('disabled', false);
    $('#ChckPromediarCalificacion').prop('checked', true).attr('disabled', false);
    $('#ChckRedondearCalificacion').prop('checked', true).attr('disabled', false);
    $('#ChckTipoCalificacion').prop('checked', true).attr('disabled', false);
    var trcounter = $('#Tblperiodos tr').length;

    if (trcounter <= 1) {
    } else {
        for (var i = 1; i <= trcounter; i++) {
            $('#idRow' + i).remove();
        }

    }

    $('#modal-parametros').modal('hide');
}



function CerrarModalEquivalencia() {
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-equivalencia-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#btnNuevoEquivalencia").attr('disabled', false);
    $('#modal-equivalencia').addClass("fade");
    $('#modal-equivalencia').attr('style', "display: none;");
    $('.mymodal').attr('style', '');

    $('#modal-equivalencia').modal('hide');
}
function CerrarModalPerfilInstitucional() {
    $('.modal').attr('style', 'display: none;');
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-Perfil-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    ///$("#modal-Perfil").attr('style', "display: inline-block;");
    $("#BtnNuevoPerfil").attr('disabled', false);
    $('#modal-Perfil').addClass("fade");
    $('#modal-Perfil').attr("display: none;");
    $('.mymodal').attr('style', '');

    $('#modal-Perfil').modal('hide');
    var validator = $("form[name='FormPerfilInst']").validate();
    validator.resetForm();

    $("#txtNombrePerfilInst").val('');
    $("#txtNombrePerfilInstCom").val('');
    $("#txtClavePerfilInst").val('');
    $("#txtDomPerfilInst").val('');
    $("#txtTelefonoPerfilInst").val('');
    $("#txtFotoPerfilInst").val('');
}

function CerrarModalPeriodosCalf() {
    //Necesarios para la función de minimizar el modal
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-PeriodosCal-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#modal-PeriodoCal").attr('style', "display: inline-block;");
    $("#btnNuevoPeriodoCal").attr('disabled', false);
    $('#modal-PeriodoCal').addClass("fade");
    $('#modal-PeriodoCal').attr("display: none;");
    $('.mymodal').attr('style', '');
    //////////////////////////////////////////////////
    $('#modal-PeriodoCal').modal('hide');
    var validator = $("form[name='FormParametrosCal']").validate();
    validator.resetForm();

    $("#txtNumPeriodoC").val('');
    $("#txtFechaIPeriodosCal").val('');
    $("#txtFechaFPeriodosCal").val('');
    $("#sltParamPeriodoC").val('');
}
function CerrarModalAviso() {
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-aviso-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#btnNuevoAviso").attr('disabled', false);
    $('#modal-aviso').addClass("fade");
    $('#modal-aviso').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='formAvisos']").validate();
    validator.resetForm();
    //////////////////////////////////////////////////
    $("#txtTituloAviso").val('');
    $("#lstDirAviso").val('').trigger("chosen:updated");
    $('#lstDepartamentoAviso').val('').trigger("chosen:updated");
    $('.note-editable').empty().html('<p><br></p>');
    $("#txtFechaFAviso").val('');
    $('#txtFechaIAviso').val('');
    $("#fileFotoAviso").val('');

    $('#modal-aviso').modal('hide');
}
function CerrarModalEvento() {
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-aviso-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#btnNuevoAviso").attr('disabled', false);
    $('#modal-aviso').addClass("fade");
    $('#modal-aviso').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormEvento']").validate();
    validator.resetForm();
    //////////////////////////////////////////////////
    $("#txtTituloEvento").val('');
    $("#lstDirEvento").val('').trigger("chosen:updated");
    $('.note-editable').empty().html('<p><br></p>');
    $("#txtFechaFEvento").val('');
    $('#txtFechaIEvento').val('');


    $('#modal-evento').modal('hide');
}
function CerrarModalDocente() {
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-docente-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#BtnNuevoDocente").attr('disabled', false);
    $('#modal-docente').addClass("fade");
    $('#modal-docente').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormDocente']").validate();
    validator.resetForm();
    //////////////////////////////////////////////////
    $("#txtApaternoDocente").val('');
    $("#txtAmaternoDocente").val('');
    $("#txtDomicilioDocente").val('');
    $("#txtNombreDocente").val('');
    $('#txtCiudadDocente').val('');
    $("#txtEstadoDocente").val('');
    $("#txtCurpDocente").val('');
    $("#txtRfcDocente").val('');
    $("#lstSexoDocente").val('').trigger("chosen:updated");
    $('#txtCPDocente').val('');
    $("#txtPaisDocente").val('');
    $("#txtEmailDocente").val('');
    $("#txtFechaNacDocente").val('');
    $("#txtCedulaDocente").val('');
    $('#txtFechaIngresoDocente').val('');
    $('#txtTelDocente').val('');
    $('#fileFotoDocente').val('');

    $('#lstHoraLunesInicio').val('').trigger("chosen:updated");
    $('#lstHoraLunesFin').val('').trigger("chosen:updated");
    $("#lstHoraMartesInicio").val('').trigger("chosen:updated");
    $("#lstHoraMartesFin").val('').trigger("chosen:updated");
    $('#lstHoraMiercolesInicio').val('').trigger("chosen:updated");
    $("#lstHoraMiercolesFin").val('').trigger("chosen:updated");
    $('#lstHoraJuevesInicio').val('').trigger("chosen:updated");
    $('#lstHoraJuevesFin').val('').trigger("chosen:updated");
    $('#lstHoraViernesInicio').val('').trigger("chosen:updated");
    $('#lstHoraViernesFin').val('').trigger("chosen:updated");
    $('#lstHoraSabadoInicio').val('').trigger("chosen:updated");
    $('#lstHoraSabadoFin').val('').trigger("chosen:updated");
    $('#lstHoraDomingoInicio').val('').trigger("chosen:updated");
    $('#lstHoraDomingoFin').val('').trigger("chosen:updated");
    $('#lstEspecialDocente').val('').trigger("chosen:updated");
    $('#lstCursoDocente').val('').trigger("chosen:updated");
    $('#lstMateriaDocente').val('').trigger("chosen:updated");

    $('#txtaNotasDocente').val('');
    $('#lstEspecialDocente').val('').trigger("chosen:updated");
    $('#lstCursoDocente').val('').trigger("chosen:updated");
    $('#lstMateriaDocente').val('').trigger("chosen:updated");
    $('#modal-docente').modal('hide');
}
function CerrarModalUsuario() {

    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-usuarioPermiso-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#BtnNuevoUsuarioPermisos").attr('disabled', false);
    $('#modal-usuarioPermiso').addClass("fade");
    $('#modal-usuarioPermiso').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='formUsuarioPermiso']").validate();
    validator.resetForm();
    //////////////////////////////////////////////////
    $("#txtNomUsuarioPer").val('');
    $("#txtAPaternoUsuarioPer").val('');
    $("#txtAMaternoUsuarioPer").val('');
    $("#txtUserUsuarioPer").val('');
    $('#txtPasswordUsuarioPer').val('');
    $('#AlertConfirPassword').text('');
    $("#txtConfirmarPasswordUsuarioPer").val('');
    $("#txtEmailUsuarioPer").val('');
    $("#lstPlantelUsuario").val('').trigger("chosen:updated");
    $('#lstTipoUsuario').val('').trigger("chosen:updated");
    $('#lstPersona').val('').trigger("chosen:updated");
    $('#modal-usuarioPermiso').modal('hide');
}
function CerrarModalRol() {

    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-Roles-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#BtnNuevoRol").attr('disabled', false);
    $('#modal-Roles').addClass("fade");
    $('#modal-Roles').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormRoles']").validate();
    validator.resetForm();
    //////////////////////////////////////////////////
    $("#txtNomTipoUsuario").val('');

    $('#modal-Roles').modal('hide');
}
function CerrarModalHoraDia() {

    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-Hora-modal").removeAttr('style');
    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#BtnNuevaHora").attr('disabled', false);
    $('#modal-Hora').addClass("fade");
    $('#modal-Hora').attr('style', "display: none;");
    $('.mymodal').attr('style', '');

    $('#modal-dias').modal('hide');
}
function CerrarModalGeneraciones() {
    //Necesarios para la función de minimizar el modal
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-generacion-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#btnNuevoGeneracion").attr('disabled', false);
    $('#modal-generacion').addClass("fade");
    $('#modal-generacion').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    //////////////////////////////////////////////////

    var validator = $("form[name='formGeneraciones']").validate();
    validator.resetForm();

    $("#txtClaveGen").val('');
    $("#txtNombreGen").val('');
    $("#lstCatModalidadGen").val('').trigger("chosen:updated");
    $('#modal-generacion').modal('hide');
}

function CerrarModalGrupo() {
    //Necesarios para la función de minimizar el modal
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-grupo-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#btnNuevoGrupoE").attr('disabled', false);
    $('#modal-grupo').addClass("fade");
    $('#modal-grupo').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    //////////////////////////////////////////////////

    var validator = $("form[name='FormGrupos']").validate();
    validator.resetForm();

    $("#txtClaveGrupoE").val('');
    $("#txtNombreGrupoE").val('');
    $("#lstPlantelGrupoE").val('').trigger("chosen:updated");
    $("#lstCursoGrupoE").val('').trigger("chosen:updated");
    $("#lstCicloGrupoE").val('').trigger("chosen:updated");
    $('#modal-grupo').modal('hide');
}

/* Funciones para  Jsp Administrativo */
function CerrarModalAdministrativo() {
    /////
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-Administrativo-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#BtnNuevoAdvo").attr('disabled', false);
    $('#modal-Administrativo').addClass("fade");
    $('#modal-Administrativo').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    $('body').removeClass('modal-open');
    ////
    $("#modal-Administrativo").modal("hide");
    //Enseguida se agregara el codigo para limpiar los campos del modal;
    var validator = $("form[name='registration']").validate();
    validator.resetForm();

    $("#txtNombreAdvo").val('');
    $("#txtApaternoAdvo").val('');
    $("#txtAmaternoAdvo").val('');
    $("#txtDomicilioAdvo").val('');
    $("#txtCiudadAdvo").val('');
    $("#txtEstadoAdvo").val('');
    $("#txtCPAdvo").val('');
    $("#txtPaisAdvo").val('');
    $("#txtEmailAdvo").val('');
    $("#txtCurpAdvo").val('');
    $("#txtRfcAdvo").val('');
    $("#txtFechaNacAdvo").val('');
    $("#txtPuestoAdvo").val('');


    $('#lstSexoAdvo').val('0').trigger("chosen:updated");
    $('#lstPlantelAdvo').val('0').trigger("chosen:updated");


    $('#roundedOneTipoRecargo1').click(function () {
        $('input:checkbox[id=cbxAlergiasAdvo]').attr('checked', false);
    });
}

/* Funciones para Jsp CicloEscolar*/
function CerraModalCicloEsc() {

    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-cicloEscolar-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#btnNuevoCicloE").attr('disabled', false);
    $('#modal-cicloEscolar').addClass("fade");
    $('#modal-cicloEscolar').attr('style', "display: none;");
    $('.mymodal').attr('style', '');
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormCicloEsc']").validate();
    validator.resetForm();
    //////////////////////////////////////////////////
    $('#modal-cicloEscolar').modal('hide');
    $("#txtClaveCicloE").val('');
    $("#txtNombreCicloE").val('');
    $("#txtFechaICicloE").val('');
    $("#txtFechaFCicloE").val('');
    $("#lstPlantelUsuario").val('').trigger("chosen:updated");
    $("#lstPara").val('').trigger("chosen:updated");
}


function CerraModalAlumno() {
    //Necesarios para la función de minimizar el modal
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-Alumno-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#modal-alumno").attr('style', "display: inline-block;");
    $("#btnNuevoAlumno").attr('disabled', false);
    $('#modal-alumno').addClass("fade");
    $('#modal-alumno').attr("display: none;");
    $('.mymodal').attr('style', '');
    //////////////////////////////////////////////////
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormAlumno']").validate();
    validator.resetForm();
    //////////////////////////////////////////////////
    $('#modal-alumno').modal('hide');
    $("#txtNombreAlumno").val('');
    $("#txtApaternoAlumno").val('');
    $("#txtAmaternoAlumno").val('');
    $("#txtDomicilioAlumno").val('');
    $("#txtCiudadAlumno").val('');
    $("#txtEstadoAlumno").val('');
    $("#txtCPAlumno").val('');
    $("#txtPaisAlumno").val('');
    $("#txtEmailAlumno").val('');
    $("#txtCurpAlumno").val('');
    $("#txtFechaNacAlumno").val('');
    $("#txtRfcAlumno").val('');
    $("#txtParentescoAlumno").val('');
    $("#lstTutorAlumno").val('').trigger("chosen:updated");
    $('#lstSexoAlumno').val('').trigger("chosen:updated");
    $("#txtTutorAlumno").val('');
    $("#txtTelAlumno").val('');
    $('#lstEstatusAlumno').val('').trigger("chosen:updated");
    $('#lstPlantelAlumno').val('').trigger("chosen:updated");
    $("#txtFechaAltaAlumno").val('');
    $("#txtFechaInscAlumno").val('');
    $('#lstGrupoAlumno').val('').trigger("chosen:updated");
    $('#lstTurnoAlumno').val('').trigger("chosen:updated");
    $('#lstCicloAlumno').val('').trigger("chosen:updated");
    $('#lstCursoAlumno').val('').trigger("chosen:updated");
    $('#lstModalidadAlumno').val('').trigger("chosen:updated");
    $('#lstNivelEAlumno').val('').trigger("chosen:updated");
    $('#lstGeneracionAlumno').val('').trigger("chosen:updated");
    $("#txtaDescECronicasAdvo").val('');
    $('#lstUltGradoAlumno').val('').trigger("chosen:updated");
    $("#txtaComentariosAdAlumno").val('');
    $("#fileFotoAlumno").val('');
    $("#txtNomEmpresaAlumno").val('');
    $("#txtNomJefeAlumno").val('');
    $("#txtDireccionEmpresaAlumno").val('');
    $("#txtTelEmpresaAlumno").val('');
    $("#txtHorarioEmpreAlumno").val('');



}
function CerraModalEstAcademica() {

    //////////////////////////////////////////////////
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormEsAcademica']").validate();
    validator.resetForm();
    //Modalidad
    $("#txtNombreModalidadEst").val('');
    //Nivel Educativo
    $("#txtNombreNivelEducativoEst").val('');
    $("#txtClaveNivelEducativoEst").val('');
    $("#txtTotalCreditosNivelEducativoEst").val('');
    $("#txtTotalMateriasNivelEducativoEst").val('');
    $('#lstPara').val('').trigger("chosen:updated");
    //Curso
    $("#txtNombreCursoEst").val('');
    //Materia
    $("#txtNombreMateriaEst").val('');
    $("#txtaDescMat").val('');
    $("#txtClaveIntEst").val('');
    $("#txtClaveSEPEst").val('');
    $("#txtClaveDGTIEst").val('');
    $("#txtHrsSemanaMatEst").val('');
    $("#txtHrsTeoriaMatEst").val('');
    $("#txtHrsPracticaEst").val('');
    $("#txtTeoriaPorcEst").val('');
    $("#txtPracticaEst").val('');
    $('#lstDivNivelEdPerteneciente').val('').trigger("chosen:updated");
    $('#lstEquivalencia').val('').trigger("chosen:updated");

}
function CerrarModalExAlumno() {
    //Necesarios para la función de minimizar el modal
    $("#btnNuevoExAlumno").attr('disabled', false);
    $('#modal-Nuevoexalumno').addClass("fade");
    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormExAlumno']").validate();
    validator.resetForm();
    //////////////////////////////////////////////////
    $('#modal-Nuevoexalumno').modal('hide');
    $("#txtNombreExAl").val('');
    $("#txtApaternoExAl").val('');
    $("#txtAmaternoExAl").val('');
    $("#txtDomicilioExAl").val('');
    $("#txtCiudadExAl").val('');
    $("#txtEstadoExAl").val('');
    $("#txtPaisExAl").val('');
    $("#txtRfcExAl").val('');
    $("#txtCurpExAl").val('');
    $("#txtCPExAl").val('');
    $("#txtEmailExAl").val('');
    $("#txtFechaNacExAl").val('');
    $("#fileFotoExAl").val('');
    $("#lstSexoExAl").val('').trigger("chosen:updated");
    $('#lstTutorExAl').val('').trigger("chosen:updated");
    $("#txtTelExAl").val('');
    $("#txtParentescoExAl").val('');
    $('#txtMatriculaAlumno').val('');
}

function CerrarModalFamAlumno() {
    //Necesarios para la función de minimizar el modal
    $('.mymodal').removeClass('mini');
    $('.mymodal').removeClass('nomini');
    $('.mymodal').addClass('nomini');
    $("#li-Drag-familiarAlumno-modal").removeAttr('style');

    $("#i-minus").removeClass('fa fa-square-o').addClass('fa fa-minus');
    $("#modal-familiarAlumno").attr('style', "display: inline-block;");
    $("#btnNuevoFamAlumno").attr('disabled', false);
    $('#modal-familiarAlumno').addClass("fade");
    $('#modal-familiarAlumno').attr("display: none;");
    $('.mymodal').attr('style', '');
    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormFamAlumno']").validate();
    validator.resetForm();
    ////////////////////////////////////////////////////////
    $("#txtNombreFamiliarAl").val('');
    $("#DivNombreFamAlumnoIn").removeClass('open');
    $("#txtApaternoFamiliarAl").val('');
    $("#DivApaternoFamiliarAlIn").removeClass('open');
    $("#txtAmaternoFamiliarAl").val('');
    $("#DivAmaternoFamiliarAlIn").removeClass('open');
    $("#txtParentescoFamiliarAl").val('');
    $("#DivParentescoFamiliarAlIn").removeClass('open');
    $("#txtTelFamiliarAl").val('');
    $("#DivTelFamiliarAlIn").removeClass('open');
    $("#txtEmailFamiliarAl").val('');
    $("#DivEmailFamiliarAlIn").removeClass('open');
    $("#txtDomicilioFamiliarAl").val('');
    $("#DivDomicilioFamiliarAlIn").removeClass('open');
    $('#modal-familiarAlumno').modal('hide');

}

function CerraModalDocumento() {

//    //////////////////////////////////////////////////
//    //Aquí se resetea el puto form!!!!
    var validator = $("form[name='FormDocumento']").validate();
    validator.resetForm();
//    //////////////////////////////////////////////////
//    $('#modal-agregarDocumento').modal('hide');
//

    $("#lstDocAlumno").val('').trigger("chosen:updated");
    $('#txtOriginalReqAlumno').val('');
    $("#txtCopiaReqAlumno").val('');
    $("#txtOriginalRecAlumno").val('');
    $('#txtCopiaRecAlumno').val('');
    $('#lstTipoDocAlumno').val('').trigger("chosen:updated");
    $("#txtFechaDocRecibido").val('');
    $("#txtNomRecAlumno").val('');
    $('#txtaObsDocAlumno').val('');


}

function CerrarModalAlumnoATutor() {
    $('#modal-AlumnoAdd').modal('hide');
    $('#modal-familiarAlumno').modal("show");
}

function CerrarModalTareaAlumno() {
    var validator = $("form[name='FormEntregarTarea']").validate();
    validator.resetForm();
    $("#modal-subirTarea").modal("hide");
}
/*
 * Dentro de esta función realizamos una gestion de acciones en los modals,
 * en que momento tienen que cerrarse en determinado button o acciones dentro de los JSP(Modulo del sistema).
 */
var bandera;
function AccionesModalsEquivalenciaJSP() {
    bandera = document.getElementById('bandera').value; /* la variable bandera obtiene el valor asignado al input con id='bandera' dentro del JSP entrante */
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalCatEquivalencia();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalCatEquivalencia();
            break;
        case '3':
            $('#bandera').val('');
            CerrarModalEquivalencia();
            break;
        case '4':
            $('#bandera').val('');
            CerrarModalEquivalencia();
            break;
        default:
            $('#bandera').val('');
    }
}

function AccionesModalsAdministrativoJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalAdministrativo();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalAdministrativo();
        default:
            $('#bandera').val('');
    }
}
function AccionesModalsAvisoJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalAviso();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalAviso();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}
function AccionesModalsCalendarioJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalEvento()
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalEvento();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}

function AccionesModalsDocenteJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalDocente();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalDocente();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}
function AccionesModalsUsuarioJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalUsuario();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalUsuario();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}
function AccionesModalsRolJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalRol();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalRol();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}
function AccionesModalsHoraDiaJSP() {
    bandera = document.getElementById('bandera').value;

    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalHoraDia();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalHoraDia();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}
function AccionesModalsCicloEscJSP() {

    bandera = document.getElementById('bandera').value;

    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerraModalCicloEsc();
            break;
        case '2':
            $('#bandera').val('');
            CerraModalCicloEsc();
            break;
        default :
            $('#bandera').val('');
            break;

    }
}
function AccionesModalsIncorporacionesJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerraModalIncor();
            break;
        case '2':
            $('#bandera').val('');
            CerraModalIncor();
            break;
        default :
            $('#bandera').val('');
            break;

    }
}
function AccionesModalsAlumnosJSP() {
    bandera = document.getElementById('bandera').value;
    // alert(bandera);
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerraModalAlumno();
            break;
        case '2':
            $('#bandera').val('');
            CerraModalAlumno();
            break;
             case '22':
            $('#bandera').val('');
            CerraModalAlumno();
            break;
        case '9':
            $('#bandera').val('');
            CerraModalDocumento();
            break;
        case '10':
            $('#bandera').val('');
            CerraModalDocumento();
            break;
        case '11':
            $('#bandera').val('');
            CerraModalDocumento();
            break;
        case '5':
            CerrarModalMensajeSoporte();
            $('#bandera').val('');
            break;
        default :
            $('#bandera').val('');
            break;

    }
}
function AccionesModalsEstAcademicaJSP() {
    bandera = document.getElementById('txtBanderaId').value;

    switch (bandera) {
        case '1':
            $('#txtBanderaId').val('');
            CerraModalEstAcademica();
            break;
             case '5':
            $('#txtBanderaId').val('');
            CerraModalEstAcademica();
            break;
              case '15':
            $('#txtBanderaId').val('');
            CerraModalEstAcademica();
            break;

        default :
            $('#txtBanderaId').val('');
            break;

    }
}
function AccionesModalsExAlumnosJSP() {
    bandera = document.getElementById('bandera').value;
    alert(bandera + "dfgf");
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalExAlumno();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalExAlumno();
            break;
        default :
            $('#bandera').val('');
            break;

    }
}

function AccionesModalsFamAlumnosJSP() {
    bandera = document.getElementById('bandera').value;
    //alert(bandera);
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalFamAlumno();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalFamAlumno();
            break;
        case '3':
            $('#bandera').val('');
            CerrarModalAlumnoATutor();
            break;
        default :
            $('#bandera').val('');
            break;

    }
}
function AccionesModalsPerfilInstitucionalJSP() {
    var ban = document.getElementById('bandera').value;
    switch (ban) {
        case '1':
            $('#bandera').val('');
            CerrarModalPerfilInstitucional();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalPerfilInstitucional();
            break;
        case '5':
            $('#bandera').val('');
        case '3':
            break;
        default :
            $('#bandera').val('');
            break;
    }
}

function AccionesModalsParamCalifJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            CerrarModalParamCalificaciones();
            break;
        case '2':
            CerrarModalParamCalificaciones();
            break;
        case '3':
            CerrarModalParamCalificaciones();
            break;
        case '5':
            $('#bandera').val('');
        default :
            $('#bandera').val('');
            break;
    }
}
function AccionesModalsPeriodoCalJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalPeriodosCalf();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalPeriodosCalf();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}

function AccionesModalsGeneracionJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '2':
            $('#bandera').val('');
            CerrarModalGeneraciones();
            break;
        case '3':
            $('#bandera').val('');
            CerrarModalGeneraciones();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}

function AccionesModalsGrupoJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalGrupo();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalGrupo();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}

function AccionesImboxControlEscolar() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {
        case '1':
            $('#bandera').val('');
            CerrarModalVerMensajeImbox();
            break;
        case '2':
            $('#bandera').val('');
            CerrarModalVerMensajeImbox();
            break;
        case '5':
            $('#bandera').val('');
            CerrarModalMensajeSoporte();
            break;
        case '7':
            $('#bandera').val('');
            CerrarModalMensajeSoporte();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}

function AccionesPageError() {
    $('#modal-mensajeReporte').modal('hide');
    window.location = "../Administrador/Bienvenida.jsp";
}

function CerrarModalVerMensajeImbox() {
    $('#modal-inboxControlEscolar').modal('hide');
}


function AccionesPerfilAlumnoJSP() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {

        case '2':
            $('#bandera').val('');
            break;
        default :
            $('#bandera').val('');
            break;
    }
}

function AccionesTareaAlumno() {
    bandera = document.getElementById('bandera').value;
    switch (bandera) {

        case '2':
            $('#bandera').val('');
            CerrarModalTareaAlumno();
            break;
        default :
            $('#bandera').val('');
            break;
    }
}
