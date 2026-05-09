from django.core.management.base import BaseCommand
from pedidos.repositories.supabase_client import OrderRepository

class Command(BaseCommand):
    help = 'Escucha cambios en tiempo real en la colección de pedidos mediante MongoDB Change Streams'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Iniciando vigilante de Change Streams..."))
        
        try:
            repo = OrderRepository()
            collection = repo.collection
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al conectar con MongoDB: {e}"))
            return

        # 1. Agregamos 'delete' a la lista de operaciones escuchadas
        pipeline = [
            {'$match': {'operationType': {'$in': ['insert', 'update', 'delete']}}}
        ]

        self.stdout.write(self.style.WARNING("Esperando cambios... (Presiona Ctrl+C para salir)"))

        try:
            with collection.watch(pipeline) as stream:
                for change in stream:
                    self.stdout.write(self.style.SUCCESS("\n¡Cambio detectado en MongoDB!"))
                    
                    op_type = change.get("operationType")
                    # El documentKey._id siempre está presente, incluso en deletes
                    doc_id = change.get("documentKey", {}).get("_id")

                    if op_type == "insert":
                        full_doc = change.get("fullDocument", {})
                        self.stdout.write(f" NUEVO PEDIDO | MongoID: {doc_id} | UUID: {full_doc.get('order_id')} | Estado: {full_doc.get('status')}")
                    
                    elif op_type == "update":
                        updated_fields = change.get("updateDescription", {}).get("updatedFields", {})
                        self.stdout.write(f" PEDIDO ACTUALIZADO | MongoID: {doc_id} | Cambios: {updated_fields}")
                    
                    # 2. Manejo del evento ELIMINADO
                    elif op_type == "delete":
                        self.stdout.write(self.style.NOTICE(f"🔴 PEDIDO ELIMINADO | MongoID: {doc_id}"))
                        self.stdout.write("Nota: En 'delete', MongoDB solo reporta el ID del documento que dejó de existir.")
                                
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("\n🛑 Vigilante detenido manualmente."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error en el Change Stream: {str(e)}"))