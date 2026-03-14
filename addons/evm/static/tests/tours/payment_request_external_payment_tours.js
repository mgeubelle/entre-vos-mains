import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_utils";

const CASE_NAME = "Dossier patient tour paiement externe";
const PAYMENT_REQUEST_NAME = "Demande tour paiement externe";

registry.category("web_tour.tours").add("evm_patient_submit_payment_request_tour", {
    url: "/my/evm/cases",
    steps: () => [
        {
            content: "Open the patient case prepared for the payment flow",
            trigger: `a:contains("${CASE_NAME}")`,
            run: "click",
        },
        {
            content: "Check the draft payment request is visible on the case detail page",
            trigger: `div.fw-semibold:contains("${PAYMENT_REQUEST_NAME}")`,
        },
        {
            content: "Submit the ready-to-send payment request",
            trigger: 'form[action*="/submit"] button[type="submit"]:contains("Soumettre la demande")',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Check the success feedback is displayed after submission",
            trigger: '.alert.alert-success:contains("La demande de paiement a ete soumise a la fondation.")',
        },
        {
            content: "Check the request is now shown as submitted",
            trigger: ".badge:contains('Soumise')",
        },
    ],
});

registry.category("web_tour.tours").add("evm_foundation_confirm_external_payment_tour", {
    url: "/odoo/action-evm.evm_payment_request_action",
    steps: () => [
        {
            content: "Open the submitted payment request from the foundation queue",
            trigger: `.o_data_row .o_data_cell:contains("${PAYMENT_REQUEST_NAME}")`,
            run: "click",
        },
        {
            content: "Check the submitted payment request form is open",
            trigger: ".o_statusbar_status .o_arrow_button_current[data-value='submitted']",
        },
        ...stepUtils.statusbarButtonsSteps("Valider", "Validate the submitted payment request"),
        {
            content: "Check the linked draft payment is available after validation",
            trigger: "button[name='action_open_payment']:contains('Voir le paiement')",
        },
        {
            content: "Check the request is now validated",
            trigger: ".o_statusbar_status .o_arrow_button_current[data-value='validated']",
        },
        ...stepUtils.statusbarButtonsSteps(
            "Confirmer paiement externe",
            "Confirm the payment made outside the platform"
        ),
        {
            content: "Check the request is marked as paid",
            trigger: ".o_statusbar_status .o_arrow_button_current[data-value='paid']",
        },
    ],
});
