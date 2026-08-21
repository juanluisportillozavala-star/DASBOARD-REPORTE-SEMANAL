// =========================================================
// Componentes JS personalizados para Dash AG Grid
// =========================================================
// Dash carga automáticamente cualquier .js dentro de /assets.
// Aquí registramos un EDITOR de celda propio para los comentarios
// de proyección: un <textarea> real donde:
//   • Alt+Enter  -> inserta salto de línea (como Excel)
//   • Enter      -> confirma y cierra la celda (como Excel)
//   • Esc        -> cancela
// Así el usuario puede dejar renglones separados en el comentario.

var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
    window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.ComentarioEditor = class {
    // se llama al iniciar la edición
    init(params) {
        this.value = params.value == null ? "" : String(params.value);

        this.eInput = document.createElement("textarea");
        this.eInput.value = this.value;
        this.eInput.rows = params.rows || 8;
        this.eInput.style.width = (params.width || 420) + "px";
        this.eInput.style.height = (params.height || 180) + "px";
        this.eInput.style.resize = "both";
        this.eInput.style.padding = "8px 10px";
        this.eInput.style.fontFamily = "inherit";
        this.eInput.style.fontSize = "14px";
        this.eInput.style.lineHeight = "1.4";
        this.eInput.style.border = "1px solid #173C73";
        this.eInput.style.borderRadius = "8px";
        this.eInput.style.boxShadow = "0 6px 20px rgba(0,0,0,0.18)";
        this.eInput.style.outline = "none";

        // Manejo de teclas estilo Excel
        this.eInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && e.altKey) {
                // Alt+Enter -> salto de línea manual
                e.preventDefault();
                e.stopPropagation();
                const ta = this.eInput;
                const ini = ta.selectionStart;
                const fin = ta.selectionEnd;
                ta.value = ta.value.substring(0, ini) + "\n" + ta.value.substring(fin);
                ta.selectionStart = ta.selectionEnd = ini + 1;
            } else if (e.key === "Enter" && !e.shiftKey) {
                // Enter solo -> confirmar y cerrar la celda
                e.preventDefault();
                params.stopEditing();
            }
            // Esc lo maneja AG Grid (cancela)
        });
    }

    // elemento que se muestra
    getGui() {
        return this.eInput;
    }

    // enfoca y coloca el cursor al final al abrir
    afterGuiAttached() {
        this.eInput.focus();
        const n = this.eInput.value.length;
        this.eInput.setSelectionRange(n, n);
    }

    // valor final que guarda la celda
    getValue() {
        return this.eInput.value;
    }

    // usar como popup (recuadro flotante)
    isPopup() {
        return true;
    }
};