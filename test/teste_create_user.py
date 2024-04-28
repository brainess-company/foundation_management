import unittest

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestUserCreation(TransactionCase):
    def setUp(self):
        super(TestUserCreation, self).setUp()
        # Preparação adicional se necessário

    def test_create_user_with_notification_type(self):
        # Criando um usuário com definição explícita para 'notification_type'
        user = self.env['res.users'].create({
            'name': 'New User',
            'login': 'new_user',
            'notification_type': 'email',  # Definindo explicitamente o tipo de notificação
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]  # Atribuindo grupo básico
        })
        self.assertEqual(user.notification_type, 'email', "O tipo de notificação deve ser 'email'.")

    def test_create_user_without_notification_type(self):
        # Este teste deve falhar se 'notification_type' não for definido
        with self.assertRaises(UserError):
            self.env['res.users'].create({
                'name': 'Another User',
                'login': 'another_user',
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]  # Atribuindo grupo básico
            })

if __name__ == '__main__':
    unittest.main()
