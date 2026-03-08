from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestEvmSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_kine = cls.env.ref("evm.group_evm_kine")
        cls.group_patient = cls.env.ref("evm.group_evm_patient")
        cls.group_fondation = cls.env.ref("evm.group_evm_fondation")
        cls.group_admin = cls.env.ref("evm.group_evm_admin")
        cls.group_portal = cls.env.ref("base.group_portal")
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_system = cls.env.ref("base.group_system")

    def test_groups_match_portal_and_internal_split(self):
        self.assertIn(self.group_portal, self.group_kine.implied_ids)
        self.assertIn(self.group_portal, self.group_patient.implied_ids)
        self.assertNotIn(self.group_user, self.group_kine.implied_ids)
        self.assertNotIn(self.group_user, self.group_patient.implied_ids)
        self.assertIn(self.group_user, self.group_fondation.implied_ids)
        self.assertIn(self.group_system, self.group_admin.implied_ids)

    def test_acl_matrix_is_defined_for_each_role(self):
        access_model = self.env["ir.model.access"]
        ir_model = self.env["ir.model"]

        expected_matrix = {
            ("evm.case", "evm.group_evm_kine"): (1, 1, 1, 0),
            ("evm.case", "evm.group_evm_patient"): (1, 0, 0, 0),
            ("evm.case", "evm.group_evm_fondation"): (1, 1, 1, 1),
            ("evm.case", "evm.group_evm_admin"): (1, 1, 1, 1),
            ("evm.payment_request", "evm.group_evm_kine"): (1, 0, 0, 0),
            ("evm.payment_request", "evm.group_evm_patient"): (1, 1, 1, 1),
            ("evm.payment_request", "evm.group_evm_fondation"): (1, 1, 1, 1),
            ("evm.payment_request", "evm.group_evm_admin"): (1, 1, 1, 1),
        }

        for (model_name, group_xmlid), expected in expected_matrix.items():
            acl = access_model.search(
                [
                    ("model_id", "=", ir_model._get(model_name).id),
                    ("group_id", "=", self.env.ref(group_xmlid).id),
                ]
            )
            self.assertEqual(len(acl), 1, f"Expected exactly one ACL for {model_name} / {group_xmlid}.")
            self.assertEqual(
                (acl.perm_read, acl.perm_write, acl.perm_create, acl.perm_unlink),
                expected,
            )

    def _create_security_fixture(self):
        kine_user = new_test_user(self.env, login="kine1", groups="evm.group_evm_kine")
        other_kine_user = new_test_user(self.env, login="kine2", groups="evm.group_evm_kine")
        patient_user = new_test_user(self.env, login="patient1", groups="evm.group_evm_patient")
        other_patient_user = new_test_user(self.env, login="patient2", groups="evm.group_evm_patient")
        fondation_user = new_test_user(self.env, login="fondation1", groups="evm.group_evm_fondation")

        case_1 = self.env["evm.case"].create(
            {
                "name": "Dossier A",
                "kine_user_id": kine_user.id,
                "patient_user_id": patient_user.id,
            }
        )
        case_2 = self.env["evm.case"].create(
            {
                "name": "Dossier B",
                "kine_user_id": other_kine_user.id,
                "patient_user_id": other_patient_user.id,
            }
        )
        payment_request_1 = self.env["evm.payment_request"].create(
            {
                "name": "Demande A",
                "case_id": case_1.id,
            }
        )
        payment_request_2 = self.env["evm.payment_request"].create(
            {
                "name": "Demande B",
                "case_id": case_2.id,
            }
        )

        return {
            "kine_user": kine_user,
            "other_kine_user": other_kine_user,
            "patient_user": patient_user,
            "other_patient_user": other_patient_user,
            "fondation_user": fondation_user,
            "case_1": case_1,
            "case_2": case_2,
            "payment_request_1": payment_request_1,
            "payment_request_2": payment_request_2,
        }

    def test_portal_users_only_see_their_records(self):
        fixture = self._create_security_fixture()

        self.assertEqual(self.env["evm.case"].with_user(fixture["kine_user"]).search([]), fixture["case_1"])
        self.assertEqual(self.env["evm.case"].with_user(fixture["patient_user"]).search([]), fixture["case_1"])
        self.assertEqual(
            self.env["evm.payment_request"].with_user(fixture["kine_user"]).search([]),
            fixture["payment_request_1"],
        )
        self.assertEqual(
            self.env["evm.payment_request"].with_user(fixture["patient_user"]).search([]),
            fixture["payment_request_1"],
        )
        self.assertEqual(self.env["evm.case"].with_user(fixture["fondation_user"]).search_count([]), 2)
        self.assertEqual(self.env["evm.payment_request"].with_user(fixture["fondation_user"]).search_count([]), 2)

    def test_portal_users_cannot_bypass_acl_or_record_rules(self):
        fixture = self._create_security_fixture()

        self.assertFalse(
            self.env["evm.case"].with_user(fixture["kine_user"]).search([("id", "=", fixture["case_2"].id)])
        )
        self.assertFalse(
            self.env["evm.payment_request"].with_user(fixture["patient_user"]).search(
                [("id", "=", fixture["payment_request_2"].id)]
            )
        )

        with self.assertRaises(AccessError):
            fixture["case_2"].with_user(fixture["kine_user"]).write({"name": "Dossier pirate"})
        with self.assertRaises(AccessError):
            fixture["case_1"].with_user(fixture["patient_user"]).write({"name": "Dossier modifie"})
        with self.assertRaises(AccessError):
            self.env["evm.case"].with_user(fixture["patient_user"]).create(
                {
                    "name": "Nouveau dossier",
                    "kine_user_id": fixture["kine_user"].id,
                    "patient_user_id": fixture["patient_user"].id,
                }
            )
        with self.assertRaises(AccessError):
            fixture["payment_request_1"].with_user(fixture["kine_user"]).write({"name": "Demande pirate"})
        with self.assertRaises(AccessError):
            self.env["evm.payment_request"].with_user(fixture["kine_user"]).create(
                {
                    "name": "Nouvelle demande",
                    "case_id": fixture["case_1"].id,
                }
            )
        with self.assertRaises(AccessError):
            fixture["payment_request_2"].with_user(fixture["patient_user"]).unlink()

    def test_allowed_operations_match_documented_acl_matrix(self):
        fixture = self._create_security_fixture()

        own_case = self.env["evm.case"].with_user(fixture["kine_user"]).create(
            {
                "name": "Dossier kine",
                "kine_user_id": fixture["kine_user"].id,
                "patient_user_id": fixture["patient_user"].id,
            }
        )
        self.assertEqual(own_case.kine_user_id, fixture["kine_user"])

        own_payment_request = self.env["evm.payment_request"].with_user(fixture["patient_user"]).create(
            {
                "name": "Demande patient",
                "case_id": fixture["case_1"].id,
            }
        )
        own_payment_request.with_user(fixture["patient_user"]).write({"name": "Demande patient maj"})
        deletable_payment_request = self.env["evm.payment_request"].create(
            {
                "name": "Demande supprimable",
                "case_id": fixture["case_1"].id,
            }
        )
        deletable_payment_request.with_user(fixture["patient_user"]).unlink()

        fondation_case = self.env["evm.case"].with_user(fixture["fondation_user"]).create(
            {
                "name": "Dossier fondation",
                "kine_user_id": fixture["other_kine_user"].id,
                "patient_user_id": fixture["other_patient_user"].id,
            }
        )
        fondation_case.with_user(fixture["fondation_user"]).write({"name": "Dossier fondation maj"})
        self.assertEqual(fondation_case.name, "Dossier fondation maj")
