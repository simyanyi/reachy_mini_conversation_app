import logging
from typing import Any, Dict

from reachy_mini.utils import create_head_pose
from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies
from reachy_mini_conversation_app.dance_emotion_moves import GotoQueueMove


logger = logging.getLogger(__name__)


class Sleep(Tool):
    """Put Reachy into sleep/rest mode with neutral pose."""

    name = "sleep"
    description = (
        "Put Reachy into sleep/rest mode. Reachy will move to a neutral, resting position "
        "with head down and arms relaxed."
    )
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> Dict[str, Any]:
        """Move to sleep/rest position."""
        logger.info("Tool call: sleep")

        try:
            movement_manager = deps.movement_manager

            # Get current state
            current_head_pose = deps.reachy_mini.get_current_head_pose()
            _, current_antennas = deps.reachy_mini.get_current_joint_positions()

            # Rest pose: head slightly down, antennas down, body neutral
            rest_head_pose = create_head_pose(0, 0, 0, 0, 20, 0, degrees=True)  # 20° pitch down
            rest_antennas = (-0.3, -0.3)  # Antennas down (negative = down)
            rest_body_yaw = 0

            # Create goto move to rest position
            goto_move = GotoQueueMove(
                target_head_pose=rest_head_pose,
                start_head_pose=current_head_pose,
                target_antennas=rest_antennas,
                start_antennas=(current_antennas[1], current_antennas[2]),  # Skip body_yaw
                target_body_yaw=rest_body_yaw,
                start_body_yaw=current_antennas[0],  # body_yaw is first
                duration=deps.motion_duration_s,
            )

            movement_manager.queue_move(goto_move)
            movement_manager.set_moving_state(deps.motion_duration_s)

            return {"status": "entering sleep mode", "position": "resting"}

        except Exception as e:
            logger.error("sleep failed: %s", e)
            return {"error": f"sleep failed: {type(e).__name__}: {e}"}
