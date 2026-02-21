"""
Servicio de Metas Financieras
"""
import logging
from typing import List, Optional
from src.database.db import db
from src.models.goal import Goal

logger = logging.getLogger(__name__)

class GoalService:
    """Servicio para gestión de metas financieras"""
    
    @staticmethod
    def get_all_goals(user_id: int) -> List[Goal]:
        """Obtiene todas las metas de un usuario"""
        query = """
            SELECT id, user_id, name, description, target_amount, 
                   current_amount, currency, target_date, category, icon, color, status
            FROM goals WHERE user_id = ? AND status IN ('active', 'completed')
            ORDER BY status, target_date
        """
        results = db.execute_query(query, (user_id,))
        goals = []
        for row in results:
            goal = Goal(
                id=row[0], user_id=row[1], name=row[2],
                description=row[3], target_amount=row[4],
                current_amount=row[5], currency=row[6],
                target_date=row[7], category=row[8],
                icon=row[9], color=row[10], status=row[11]
            )
            goals.append(goal)
        return goals
    
    @staticmethod
    def get_goal_by_id(goal_id: int) -> Optional[Goal]:
        """Obtiene una meta específica"""
        query = """
            SELECT id, user_id, name, description, target_amount,
                   current_amount, currency, target_date, category, icon, color, status
            FROM goals WHERE id = ?
        """
        results = db.execute_query(query, (goal_id,))
        if results:
            row = results[0]
            return Goal(
                id=row[0], user_id=row[1], name=row[2],
                description=row[3], target_amount=row[4],
                current_amount=row[5], currency=row[6],
                target_date=row[7], category=row[8],
                icon=row[9], color=row[10], status=row[11]
            )
        return None
    
    @staticmethod
    def create_goal(user_id: int, name: str, target_amount: float,
                   currency: str = "COP", target_date: str = "",
                   category: str = "general", description: str = "",
                   icon: str = "🎯", color: str = "#6366F1") -> Optional[int]:
        """Crea una nueva meta"""
        try:
            query = """
                INSERT INTO goals
                (user_id, name, description, target_amount, currency,
                 target_date, category, icon, color, status, current_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', 0)
            """
            goal_id = db.execute_insert(query, (
                user_id, name, description, target_amount, currency,
                target_date, category, icon, color
            ))
            logger.info(f"Meta creada: {name}")
            return goal_id
        except Exception as e:
            logger.error(f"Error creando meta: {e}")
            return None
    
    @staticmethod
    def add_progress_to_goal(goal_id: int, amount: float) -> bool:
        """Suma progreso a una meta"""
        try:
            goal = GoalService.get_goal_by_id(goal_id)
            if not goal:
                return False
            
            new_amount = min(goal.current_amount + amount, goal.target_amount)
            status = "completed" if new_amount >= goal.target_amount else "active"
            
            query = "UPDATE goals SET current_amount = ?, status = ? WHERE id = ?"
            return db.execute_update(query, (new_amount, status, goal_id))
        except Exception as e:
            logger.error(f"Error actualizando meta: {e}")
            return False
    
    @staticmethod
    def update_goal(goal_id: int, **kwargs) -> bool:
        """Actualiza una meta con los campos proporcionados"""
        try:
            allowed_fields = ['name', 'description', 'target_amount', 'currency',
                            'target_date', 'category', 'icon', 'color', 'status']
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not updates:
                return False
            
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            query = f"UPDATE goals SET {set_clause} WHERE id = ?"
            values = list(updates.values()) + [goal_id]
            
            return db.execute_update(query, values)
        except Exception as e:
            logger.error(f"Error actualizando meta: {e}")
            return False
    
    @staticmethod
    def delete_goal(goal_id: int) -> bool:
        """Elimina una meta"""
        query = "DELETE FROM goals WHERE id = ?"
        return db.execute_delete(query, (goal_id,))
    
    @staticmethod
    def get_total_goals_progress(user_id: int) -> dict:
        """Obtiene resumen de todas las metas"""
        goals = GoalService.get_all_goals(user_id)
        
        total_target = sum(g.target_amount for g in goals if g.status == "active")
        total_current = sum(g.current_amount for g in goals if g.status == "active")
        completed = len([g for g in goals if g.status == "completed"])
        
        return {
            'total_goals': len(goals),
            'active_goals': len([g for g in goals if g.status == "active"]),
            'completed_goals': completed,
            'total_target': total_target,
            'total_current': total_current,
            'overall_progress': (total_current / total_target * 100) if total_target > 0 else 0
        }
    
    @staticmethod
    def get_goals_by_category(user_id: int, category: str) -> List[Goal]:
        """Obtiene metas por categoría"""
        query = """
            SELECT id, user_id, name, description, target_amount,
                   current_amount, currency, target_date, category, icon, color, status
            FROM goals WHERE user_id = ? AND category = ? AND status = 'active'
        """
        results = db.execute_query(query, (user_id, category))
        goals = []
        for row in results:
            goal = Goal(
                id=row[0], user_id=row[1], name=row[2],
                description=row[3], target_amount=row[4],
                current_amount=row[5], currency=row[6],
                target_date=row[7], category=row[8],
                icon=row[9], color=row[10], status=row[11]
            )
            goals.append(goal)
        return goals
