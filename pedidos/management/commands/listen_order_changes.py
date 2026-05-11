import json
import select
import psycopg2
import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Escucha cambios de estado en los pedidos en tiempo real usando PostgreSQL LISTEN/NOTIFY'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Iniciando vigilante de Supabase (PostgreSQL)..."))
        
        # Obtenemos la conexión directa a la BD desde tu entorno
        db_url = os.getenv("SUPABASE_POSTGRES_URL")
        if not db_url:
            self.stdout.write(self.style.ERROR("❌ Falta la variable SUPABASE_POSTGRES_URL en el entorno o .env"))
            return

        try:
            # Nos conectamos directamente a la capa de PostgreSQL de Supabase
            conn = psycopg2.connect(db_url)
            # Autocommit es obligatorio para usar LISTEN
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Nos suscribimos al canal que creamos en el SQL
            cursor.execute("LISTEN order_status_changes;")
            self.stdout.write(self.style.WARNING(" Esperando cambios de estado... (Presiona Ctrl+C para salir)"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al conectar con PostgreSQL: {e}"))
            return

        try:
            # Bucle infinito escuchando silenciosamente
            while True:
                # select.select pone a dormir el proceso hasta que llega algo por la conexión
                if select.select([conn], [], [], 5) == ([], [], []):
                    pass
                else:
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop(0)
                        payload = json.loads(notify.payload)
                        
                        order_id = payload.get("order_id")
                        new_status = payload.get("status")

                        self.stdout.write(self.style.SUCCESS("\n¡Cambio de estado detectado!"))
                        self.stdout.write(f" PEDIDO ACTUALIZADO | UUID: {order_id} | Nuevo Estado: {new_status}")
                        
                        # ==========================================
                        # 🚀 FASE 2: INTEGRACIÓN WHATSAPP (A FUTURO)
                        # ==========================================
                        # Aquí es exactamente donde harás:
                        # if new_status == 'SHIPPED':
                        #     send_whatsapp_message(order_id, "¡Tu pedido va en camino!")
                        # ==========================================

        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("\n🛑 Vigilante detenido manualmente."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n Error en el flujo de conexión: {str(e)}"))
        finally:
            if conn:
                cursor.close()
                conn.close()