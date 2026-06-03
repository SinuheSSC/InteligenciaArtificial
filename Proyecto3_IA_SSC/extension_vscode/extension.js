const vscode = require("vscode");

const API_URL = "http://127.0.0.1:5000/autocompletar";

function activate(context) {
    let disposable = vscode.commands.registerCommand(
        "autocompletado-rnn-c.autocompletar",
        async function () {
            let editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage("No hay un editor abierto");
                return;
            }

            let documento = editor.document;
            let cursorPos = editor.selection.active;
            let linea = cursorPos.line;
            let rango = new vscode.Range(linea, 0, linea, cursorPos.character);
            let codigo = documento.getText(rango);

            if (!codigo || codigo.trim() === "") {
                vscode.window.showErrorMessage("Escribe algo antes de autocompletar");
                return;
            }

            let statusMsg = vscode.window.setStatusBarMessage(
                "$(sync~spin) RNN generando autocompletado..."
            );

            try {
                let respuesta = await fetch(API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        codigo: codigo,
                        max_tokens: 200,
                    }),
                });

                if (!respuesta.ok) {
                    statusMsg.dispose();
                    vscode.window.showErrorMessage(
                        "Error en el servidor RNN: " + respuesta.status
                    );
                    return;
                }

                let datos = await respuesta.json();
                let completado = datos.completado;

                statusMsg.dispose();

                if (!completado || completado.trim() === "") {
                    vscode.window.showInformationMessage(
                        "La RNN no genero codigo nuevo"
                    );
                    return;
                }

                await editor.edit(function (edicion) {
                    let posicion = editor.selection.active;
                    edicion.insert(posicion, completado);
                });

                vscode.window.showInformationMessage(
                    "Completado insertado (" + completado.length + " caracteres)"
                );
            } catch (error) {
                statusMsg.dispose();
                const mensaje =
                    error.message === "fetch failed"
                        ? "No se pudo conectar con la API. ¿Ejecutaste 'python servidor_api.py' primero?"
                        : "Error: " + error.message;
                vscode.window.showErrorMessage(mensaje);
            }
        }
    );

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate,
};
