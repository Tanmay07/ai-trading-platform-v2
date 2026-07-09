import logging
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from bootstrap_engine.state import BootstrapRun, SessionLocal, init_db
from bootstrap_engine.steps import (
    step1_universe, step2_download, step3_validation, step4_features,
    step5_labels, step6_dataset, step7_train, step8_ensemble,
    step9_validate, step10_register, step11_predict, step12_recommendation
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BootstrapManager")

class BootstrapManager:
    """Orchestrates the entire Phase E1 pipeline from steps 1 to 12."""
    
    _background_task = None
    
    @classmethod
    def start_pipeline(cls):
        """Starts or resumes the pipeline in the background."""
        if cls._background_task and not cls._background_task.done():
            logger.warning("Pipeline is already running.")
            return {"status": "Running", "message": "Pipeline already active."}
            
        init_db()
        db = SessionLocal()
        
        # Check for active or interrupted run
        run = db.query(BootstrapRun).filter(BootstrapRun.status.in_(["Pending", "Running", "Failed"])).first()
        if not run:
            run = BootstrapRun(status="Running", current_step=1)
            db.add(run)
            db.commit()
            db.refresh(run)
        else:
            run.status = "Running"
            db.commit()
            
        cls._background_task = asyncio.create_task(cls._execute(run.id))
        return {"status": "Started", "run_id": run.id, "current_step": run.current_step}
        
    @classmethod
    async def _execute(cls, run_id: int):
        db = SessionLocal()
        run = db.query(BootstrapRun).filter(BootstrapRun.id == run_id).first()
        
        try:
            steps = [
                step1_universe.execute, step2_download.execute, step3_validation.execute,
                step4_features.execute, step5_labels.execute, step6_dataset.execute,
                step7_train.execute, step8_ensemble.execute, step9_validate.execute,
                step10_register.execute, step11_predict.execute, step12_recommendation.execute
            ]
            
            for i in range(run.current_step - 1, len(steps)):
                step_num = i + 1
                logger.info(f"--- Starting Step {step_num} ---")
                
                # Execute step
                if asyncio.iscoroutinefunction(steps[i]):
                    await steps[i](run_id, db)
                else:
                    steps[i](run_id, db)
                    
                # Update progress
                run.current_step = step_num + 1
                db.commit()
                logger.info(f"--- Completed Step {step_num} ---")
                
            run.status = "Completed"
            run.end_time = datetime.utcnow()
            db.commit()
            logger.info("Bootstrap Pipeline fully completed!")
            
        except Exception as e:
            logger.error(f"Pipeline failed at step {run.current_step}: {str(e)}")
            run.status = "Failed"
            run.error_message = str(e)
            db.commit()
        finally:
            db.close()
            
    @classmethod
    def get_status(cls):
        db = SessionLocal()
        run = db.query(BootstrapRun).order_by(BootstrapRun.id.desc()).first()
        db.close()
        if not run:
            return {"status": "Not Started"}
        return {
            "run_id": run.id,
            "status": run.status,
            "current_step": min(run.current_step, run.total_steps),
            "total_steps": run.total_steps,
            "error": run.error_message,
            "start_time": run.start_time
        }
