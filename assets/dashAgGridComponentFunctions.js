// =========================================================
// Componentes / funciones JS para Dash AG Grid
// =========================================================
// Dash carga automáticamente cualquier .js dentro de /assets.
//
// EDITORES de celda  -> window.dashAgGridFunctions
//   "cellEditor": {"function": "ComentarioEditor"}
// RENDERERS de celda -> window.dashAgGridComponentFunctions
//   "cellRenderer": "ComentarioRenderer"
//
// ComentarioEditor: editor de texto ENRIQUECIDO (negrita, subrayado,
// resaltado y tamaño de letra) usando un div contenteditable. Guarda
// el contenido como HTML. Compatible hacia atrás: los comentarios
// viejos en texto plano se muestran igual.
//   • Enter  -> salto de línea normal (no cierra la edición)
//   • Botón "Guardar y cerrar" -> confirma y cierra
//   • Esc    -> cancela (comportamiento por defecto de AG Grid)

var dagfuncs = (window.dashAgGridFunctions =
    window.dashAgGridFunctions || {});
var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
    window.dashAgGridComponentFunctions || {});


// ---------------------------------------------------------
// Utilidad: ¿el valor guardado ya es HTML o es texto plano?
// (los comentarios viejos son texto plano y hay que respetar
//  sus saltos de línea al mostrarlos)
// ---------------------------------------------------------
function _pareceHTML(txt) {
    return /<[a-z][\s\S]*>/i.test(txt || "");
}

function _escaparHTML(txt) {
    var d = document.createElement("div");
    d.textContent = txt == null ? "" : String(txt);
    return d.innerHTML;
}

// texto plano -> HTML conservando saltos de línea
function _textoPlanoAHTML(txt) {
    return _escaparHTML(txt).replace(/\n/g, "<br>");
}


// =========================================================
// EDITOR ENRIQUECIDO
// =========================================================
dagfuncs.ComentarioEditor = class {
    init(params) {
        this.params = params;
        var valor = params.value == null ? "" : String(params.value);
        var self = this;

        // ---- contenedor (recuadro) ----
        this.eGui = document.createElement("div");
        this.eGui.style.display = "flex";
        this.eGui.style.flexDirection = "column";
        this.eGui.style.width = (params.width || 500) + "px";
        this.eGui.style.background = "#FFFFFF";
        this.eGui.style.border = "1px solid #173C73";
        this.eGui.style.borderRadius = "8px";
        this.eGui.style.boxShadow = "0 8px 24px rgba(0,0,0,0.20)";
        this.eGui.style.padding = "10px";

        // CLAVE: evitar que un clic DENTRO del editor (barra, área,
        // botón) sea interpretado por AG Grid como "clic afuera" y
        // cierre la edición al instante. Detenemos la propagación del
        // mousedown en todo el recuadro.
        this.eGui.addEventListener("mousedown", function (e) {
            e.stopPropagation();
        });
        this.eGui.addEventListener("click", function (e) {
            e.stopPropagation();
        });

        // ---- barra de herramientas ----
        var toolbar = document.createElement("div");
        toolbar.style.display = "flex";
        toolbar.style.flexWrap = "wrap";
        toolbar.style.gap = "4px";
        toolbar.style.marginBottom = "8px";
        toolbar.style.borderBottom = "1px solid #EEF2F7";
        toolbar.style.paddingBottom = "8px";

        // helper: crea un botón de formato
        function botonFmt(html, titulo, accion) {
            var b = document.createElement("button");
            b.type = "button";
            b.innerHTML = html;
            b.title = titulo;
            b.style.minWidth = "32px";
            b.style.height = "30px";
            b.style.border = "1px solid #CBD5E1";
            b.style.borderRadius = "5px";
            b.style.background = "#F8FAFD";
            b.style.color = "#173C73";
            b.style.cursor = "pointer";
            b.style.fontSize = "14px";
            b.style.fontWeight = "600";
            // usar mousedown + preventDefault para NO perder la selección
            b.addEventListener("mousedown", function (e) {
                e.preventDefault();
                accion();
                self.eInput.focus();
            });
            return b;
        }

        // Negrita / Subrayado / Cursiva / Tachado
        toolbar.appendChild(botonFmt("<b>N</b>", "Negrita",
            function () { document.execCommand("bold"); }));
        toolbar.appendChild(botonFmt("<u>S</u>", "Subrayado",
            function () { document.execCommand("underline"); }));
        toolbar.appendChild(botonFmt("<i>C</i>", "Cursiva",
            function () { document.execCommand("italic"); }));

        // Resaltar (amarillo) y quitar resaltado
        toolbar.appendChild(botonFmt(
            "<span style='background:#FFE066;padding:0 4px;'>R</span>",
            "Resaltar",
            function () { document.execCommand("hiliteColor", false, "#FFE066"); }));
        toolbar.appendChild(botonFmt(
            "<span style='text-decoration:line-through;'>R</span>",
            "Quitar resaltado",
            function () { document.execCommand("hiliteColor", false, "transparent"); }));

        // Color de letra (azul de marca)
        toolbar.appendChild(botonFmt(
            "<span style='color:#173C73;'>A</span>",
            "Color azul",
            function () { document.execCommand("foreColor", false, "#173C73"); }));
        toolbar.appendChild(botonFmt(
            "<span style='color:#C0392B;'>A</span>",
            "Color rojo",
            function () { document.execCommand("foreColor", false, "#C0392B"); }));

        // Tamaño de letra: más chica / normal / más grande
        // execCommand fontSize usa escala 1..7 (2=chica, 3=normal, 5=grande)
        toolbar.appendChild(botonFmt(
            "<span style='font-size:11px;'>A-</span>", "Letra más chica",
            function () { document.execCommand("fontSize", false, "2"); }));
        toolbar.appendChild(botonFmt(
            "<span style='font-size:14px;'>A</span>", "Letra normal",
            function () { document.execCommand("fontSize", false, "3"); }));
        toolbar.appendChild(botonFmt(
            "<span style='font-size:18px;'>A+</span>", "Letra más grande",
            function () { document.execCommand("fontSize", false, "5"); }));

        // Quitar todo el formato
        toolbar.appendChild(botonFmt(
            "&#10005;", "Quitar formato",
            function () { document.execCommand("removeFormat"); }));

        // ---- área editable (contenteditable) ----
        this.eInput = document.createElement("div");
        this.eInput.contentEditable = "true";
        this.eInput.style.width = "100%";
        this.eInput.style.minHeight = (params.height || 180) + "px";
        this.eInput.style.maxHeight = "340px";
        this.eInput.style.overflowY = "auto";
        this.eInput.style.padding = "8px 10px";
        this.eInput.style.fontFamily = "inherit";
        this.eInput.style.fontSize = "14px";
        this.eInput.style.lineHeight = "1.5";
        this.eInput.style.border = "1px solid #CBD5E1";
        this.eInput.style.borderRadius = "6px";
        this.eInput.style.outline = "none";
        this.eInput.style.boxSizing = "border-box";
        this.eInput.style.textAlign = "left";

        // cargar el valor: si ya es HTML se pone tal cual; si es texto
        // plano (comentario viejo) se convierte conservando saltos.
        if (_pareceHTML(valor)) {
            this.eInput.innerHTML = valor;
        } else {
            this.eInput.innerHTML = _textoPlanoAHTML(valor);
        }

        // Enter = salto de línea normal (que AG Grid no cierre la edición)
        this.eInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.stopPropagation();
            }
        });

        // ---- barra inferior con botón guardar ----
        var barra = document.createElement("div");
        barra.style.display = "flex";
        barra.style.justifyContent = "space-between";
        barra.style.alignItems = "center";
        barra.style.marginTop = "8px";

        var ayuda = document.createElement("span");
        ayuda.textContent = "Selecciona texto y usa la barra para dar formato";
        ayuda.style.fontSize = "12px";
        ayuda.style.color = "#6C757D";

        this.eBtn = document.createElement("button");
        this.eBtn.type = "button";
        this.eBtn.textContent = "Guardar y cerrar";
        this.eBtn.style.backgroundColor = "#173C73";
        this.eBtn.style.color = "#FFFFFF";
        this.eBtn.style.border = "none";
        this.eBtn.style.padding = "8px 18px";
        this.eBtn.style.borderRadius = "6px";
        this.eBtn.style.fontWeight = "600";
        this.eBtn.style.cursor = "pointer";
        this.eBtn.addEventListener("click", function () {
            self.params.stopEditing();
        });

        barra.appendChild(ayuda);
        barra.appendChild(this.eBtn);

        this.eGui.appendChild(toolbar);
        this.eGui.appendChild(this.eInput);
        this.eGui.appendChild(barra);
    }

    getGui() {
        return this.eGui;
    }

    afterGuiAttached() {
        var self = this;
        // enfocar con un pequeño retraso: garantiza que el popup ya
        // está montado en el DOM antes de pedir el foco y colocar el
        // cursor. Sin esto, algunos navegadores no dan el foco y AG
        // Grid cierra el editor de inmediato.
        setTimeout(function () {
            self.eInput.focus();
            try {
                var rango = document.createRange();
                rango.selectNodeContents(self.eInput);
                rango.collapse(false);
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(rango);
            } catch (e) {}
        }, 30);
    }

    // AG Grid llama focusIn cuando el editor debe tomar el foco;
    // ayuda a que no se cierre por "pérdida de foco".
    focusIn() {
        this.eInput.focus();
    }

    getValue() {
        // devolver HTML; si quedó vacío, cadena vacía
        var html = this.eInput.innerHTML.trim();
        if (html === "<br>" || html === "<div><br></div>") {
            return "";
        }
        return html;
    }

    isPopup() {
        return true;
    }
};


// =========================================================
// RENDERER: muestra el comentario con su formato (HTML) dentro
// de la celda. Para comentarios viejos (texto plano) respeta los
// saltos de línea.
// =========================================================
dagcomponentfuncs.ComentarioRenderer = function (props) {
    var valor = props.value == null ? "" : String(props.value);
    var html = _pareceHTML(valor) ? valor : _textoPlanoAHTML(valor);
    // React.createElement con dangerouslySetInnerHTML (React viene en
    // el scope global de dash-ag-grid para las funciones de componente)
    return React.createElement("div", {
        style: {
            whiteSpace: "normal",
            lineHeight: "1.4",
            padding: "4px 0",
            textAlign: "left",
        },
        dangerouslySetInnerHTML: { __html: html },
    });
};
