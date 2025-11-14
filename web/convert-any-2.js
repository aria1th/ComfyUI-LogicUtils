/** @typedef {import('@comfyorg/comfyui-frontend-types').ComfyApp} ComfyApp */
/** @typedef {import('@comfyorg/litegraph').LiteGraph} LiteGraph */
/** @typedef {import("@comfyorg/litegraph/dist/interfaces").INodeInputSlot} INodeInputSlot */
/** @typedef {import("@comfyorg/litegraph/dist/interfaces").INodeOutputSlot} INodeOutputSlot */
/** @typedef {import("@comfyorg/litegraph/dist/interfaces").ISlotType} ISlotType */
/** @typedef {import("@comfyorg/litegraph/dist/LLink").LLink} LLink */
/** @typedef {import("@comfyorg/litegraph/dist/types/serialisation").SubgraphIO} SubgraphIO */
/** @typedef {import("@comfyorg/litegraph/dist/LGraphNode").LGraphNode} LGraphNode */
/** @typedef {import("../../typings/ComfyNode").ComfyNode} ComfyNode */

import { app } from "../../scripts/app.js";

/**
 * Chains a callback function to an object's property.
 * @param {object} object
 * @param {string} property
 * @param {function} callback
 */
function chainCallback(object, property, callback) {
    if (!object) {
        console.error("Tried to add callback to a non-existent object");
        return;
    }
    if (property in object) {
        const callback_orig = object[property];
        object[property] = function () {
            const r = callback_orig?.apply(this, arguments);
            callback.apply(this, arguments);
            return r;
        };
    } else {
        object[property] = callback;
    }
}

app.registerExtension({
    name: "ovum.convertany2.listish",
    /**
     * This method is triggered when a new node is created in the application.
     * It establishes and enforces rules for dynamic input management for specific node types,
     * ensuring correct behavior during node creation, configuration, and connection changes.
     *
     * @param {Object} node - The newly created node instance.
     * @param {Object} app - The application instance where the node is being registered or managed.
     * @return {Promise<void>} Resolves when the node's dynamic input rules and behaviors are properly initialized.
     */
    // nodeCreated(node, app) {},
    /**
     * Handles the initialization and dynamic management of node inputs for a specific node type.
     * This method is designed to enforce specific rules regarding dynamic inputs for nodes,
     * ensuring proper behavior during creation, configuration, and connection changes.
     *
     * @param {Object} nodeType - The type definition of the node being registered.
     * @param {Object} nodeData - The data associated with the node being registered.
     * @param {Object} appInstance - The application instance where the node is being registered.
     * @return {Promise<void>} Resolves when the dynamic input management is set up for the specified node type.
     */
    async beforeRegisterNodeDef(nodeType, nodeData, appInstance) {
        // Target the Python class that supports many dynamic inputs
        if (!nodeType.comfyClass.match(/^ConvertAny2.*(Tuple|Dict|List|Set)$/)) {
            return;
        }
        /** @type {ComfyApp} */
        // this.nodeCreated()
        chainCallback(nodeType.prototype, "onNodeCreated", function () {
            /** @type {ComfyNode} */
            const node = this;
            /** @type {LGraph|Subgraph} */
            /** Called for each connection that is created, updated, or removed. This includes "restored" connections when deserialising. */
            chainCallback(node, "onConnectionsChange",
                /**
                 * @this {ComfyNode}
                 * @param {ISlotType} type
                 * @param {number} index
                 * @param {boolean} connected
                 * @param {LLink|null|undefined} link_info
                 * @param {INodeInputSlot|INodeOutputSlot|SubgraphIO} inputOrOutput
                 */
                function (type, index, connected, link_info, inputOrOutput) {
                    if (!link_info || type !== LiteGraph.INPUT) return;

                    const stackTrace = new Error().stack;

                    if (!connected) {
                        if (!stackTrace.includes('LGraphNode.prototype.connect') &&
                            !stackTrace.includes('convertToSubgraph') &&
                            !stackTrace.includes('pasteFromClipboard') &&
                            !stackTrace.includes('LGraphNode.connect') &&
                            !stackTrace.includes('loadGraphData')) {
                            this.removeInput(index);
                            // this.inputs[index].label = this.outputs[index].label = "any";
                        }
                    }

                    let inputIndex = 1;
                    this.inputs.forEach(input => {
                        const newName = `input_${inputIndex}`;
                        if (input.name !== newName) {
                            input.name = newName;
                        }
                        inputIndex++;
                    });

                    const lastInput = this.inputs[this.inputs.length - 1];
                    if (lastInput?.link != null) {
                        this.addInput(`input_${inputIndex}`, "*");
                    }

                    this.setDirtyCanvas(true, true);
            });
        });
    },
});
