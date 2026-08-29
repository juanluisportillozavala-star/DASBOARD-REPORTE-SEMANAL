// =========================================================
// Componentes / funciones JS para Dash AG Grid
// =========================================================
// Dash carga automáticamente cualquier .js dentro de /assets.
//
// IMPORTANTE: los EDITORES de celda personalizados van en
// window.dashAgGridFunctions (NO en dashAgGridComponentFunctions,
// que es para renderers). Se referencian desde Python como
//   "cellEditor": {"function": "ComentarioEditor"}
//
// Editor de comentarios de proyección: un <textarea> real dentro
// de un recuadro, con botón "Guardar y cerrar".
//   • Enter  -> salto de línea NORMAL
//   • Botón "Guardar y cerrar" o clic afuera -> confirma y cierra
//   • Esc    -> cancela

var dagfuncs = (window.dashAgGridFunctions =
    window.dashAgGridFunctions || {});

dagfuncs.ComentarioEditor = class {
    init(params) {
        this.params = params;
        var valor = params.value == null ? "" : String(params.value);

        // ---- contenedor (recuadro) ----
        this.eGui = document.createElement("div");
        this.eGui.style.display = "flex";
        this.eGui.style.flexDirection = "column";
        this.eGui.style.width = (params.width || 480) + "px";
        this.eGui.style.background = "#FFFFFF";
        this.eGui.style.border = "1px solid #173C73";
        this.eGui.style.borderRadius = "8px";
        this.eGui.style.boxShadow = "0 8px 24px rgba(0,0,0,0.20)";
        this.eGui.style.padding = "10px";

        // ---- textarea ----
        this.eInput = document.createElement("textarea");
        this.eInput.value = valor;
        this.eInput.style.width = "100%";
        this.eInput.style.height = (params.height || 200) + "px";
        this.eInput.style.resize = "both";
        this.eInput.style.padding = "8px 10px";
        this.eInput.style.fontFamily = "inherit";
        this.eInput.style.fontSize = "14px";
        this.eInput.style.lineHeight = "1.5";
        this.eInput.style.border = "1px solid #CBD5E1";
        this.eInput.style.borderRadius = "6px";
        this.eInput.style.outline = "none";
        this.eInput.style.boxSizing = "border-box";

        // Enter = salto de línea normal: evitar que AG Grid capture
        // la tecla y cierre la edición.
        this.eInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.stopPropagation();
            }
        });

        // ---- barra inferior con botón ----
        var barra = document.createElement("div");
        barra.style.display = "flex";
        barra.style.justifyContent = "space-between";
        barra.style.alignItems = "center";
        barra.style.marginTop = "8px";

        var ayuda = document.createElement("span");
        ayuda.textContent = "Enter = nuevo renglón";
        ayuda.style.fontSize = "12px";
        ayuda.style.color = "#6C757D";

        var self = this;
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

        this.eGui.appendChild(this.eInput);
        this.eGui.appendChild(barra);
    }

    getGui() {
        return this.eGui;
    }

    afterGuiAttached() {
        this.eInput.focus();
        var n = this.eInput.value.length;
        this.eInput.setSelectionRange(n, n);
    }

    getValue() {
        return this.eInput.value;
    }

    isPopup() {
        return true;
    }
};