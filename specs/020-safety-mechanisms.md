# Safety Mechanisms Specification (Lightweight)

**Type**: System Behavior  
**Interactions**: All Agents, Expert Interface, Monitoring System

## Prerequisites
- Read: Core Principles Specification (002-core-principles.md)
- Read: Reflection Agent Specification (008-reflection-agent.md)
- Read: Expert Intervention Points Specification (018-expert-intervention-points.md)

## Overview

The Lightweight Safety Mechanisms provide monitoring and logging capabilities to track research patterns while leveraging built-in LLM safety features. This system focuses on transparency and user control rather than hard blocking.

## Design Philosophy

1. **Monitor, Don't Block**: Log and track patterns for review
2. **Trust the LLM**: Rely on model's built-in safety training
3. **User Control**: Configurable trust levels and easy disable
4. **Minimal Overhead**: Fast, non-intrusive checks
5. **Audit Trail**: Comprehensive logging for accountability

## Safety Configuration

### Trust Levels
```json
{
  "trust_levels": {
    "trusted": {
      "description": "Minimal logging, no blocking",
      "safety_checks": false,
      "logging_level": "minimal"
    },
    "standard": {
      "description": "Full logging, advisory warnings",
      "safety_checks": true,
      "logging_level": "detailed"
    },
    "restricted": {
      "description": "Enhanced monitoring, possible delays",
      "safety_checks": true,
      "logging_level": "verbose",
      "review_threshold": 0.5
    }
  }
}
```

### Global Configuration
```json
{
  "safety": {
    "enabled": true,
    "default_trust_level": "standard",
    "log_only_mode": true,
    "log_directory": ".aicoscientist/safety_logs/",
    "blocking_threshold": 0.95
  }
}
```

## Safety Evaluation Levels (Monitoring Focus)

### Level 1: Research Goal Logging

**Trigger**: Upon receiving any research goal input  
**Process**: Log goal and metadata  
**Decision**: Always ACCEPT (unless LLM refuses)

#### Input/Output
```json
{
  "input": {
    "research_goal": "string",
    "context": {
      "domain": "string",
      "user_role": "string", 
      "timestamp": "datetime"
    }
  },
  "output": {
    "decision": "SAFE",
    "safety_score": 1.0,
    "reasoning": "Logged for monitoring",
    "logged": true,
    "log_id": "string"
  }
}
```

### Level 2: Hypothesis Monitoring

**Trigger**: After each hypothesis generation  
**Process**: Log hypothesis details  
**Decision**: Track patterns without filtering

#### Monitoring Data
```json
{
  "hypothesis_id": "string",
  "timestamp": "datetime",
  "content_hash": "string",
  "metadata": {
    "research_goal_id": "string",
    "generation_context": "object"
  }
}
```

### Level 3: Pattern Tracking

**Trigger**: Periodic analysis (configurable)  
**Process**: Identify trends without intervention  
**Action**: Generate reports for review

#### Pattern Report
```json
{
  "report_id": "string",
  "period": "string",
  "patterns_observed": [
    {
      "pattern_type": "string",
      "frequency": "integer",
      "examples": ["log_id_1", "log_id_2"]
    }
  ],
  "recommendations": "string"
}
```

### Level 4: Audit Reports

**Trigger**: On-demand or scheduled  
**Process**: Comprehensive activity summary  
**Output**: Human-readable audit trail

## Safety Boundaries (Advisory Only)

### Logging Categories
1. **Research Goals**: All goals with timestamps and context
2. **Hypothesis Generation**: Content hashes and metadata
3. **Pattern Emergence**: Trend identification
4. **User Interactions**: Commands and overrides

### Privacy Considerations
- Hash sensitive content rather than storing verbatim
- Configurable retention periods
- User-controlled data deletion

## Integration Points

### Supervisor Agent
- Logs all task assignments
- No blocking of tasks based on safety

### Generation Agent
- Logs generated hypotheses
- Relies on LLM's judgment

### Reflection Agent
- Includes safety score (always high in lightweight mode)
- Notes any concerns raised by LLM

### Expert Interface
- Access to safety logs and reports
- Configuration override capabilities

## Implementation Classes

### SafetyLogger
```python
class SafetyLogger:
    """Lightweight safety monitoring system."""
    
    def __init__(self, config: SafetyConfig):
        self.enabled = config.enabled
        self.trust_level = config.trust_level
        self.log_only = config.log_only_mode
    
    async def log_research_goal(self, goal: str, context: dict) -> SafetyCheck:
        """Log research goal without evaluation."""
        if not self.enabled:
            return SafetyCheck(
                decision=SafetyLevel.SAFE,
                safety_score=1.0,
                reasoning="Safety logging disabled"
            )
        
        # Log the goal
        log_entry = await self._create_log_entry(goal, context)
        
        return SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=1.0,
            reasoning="Logged for monitoring",
            metadata={"log_id": log_entry.id}
        )
```

### SafetyConfig
```python
@dataclass
class SafetyConfig:
    """Configuration for lightweight safety system."""
    enabled: bool = True
    trust_level: str = "standard"
    log_only_mode: bool = True
    log_directory: Path = Path(".aicoscientist/safety_logs")
    blocking_threshold: float = 0.95
    retention_days: int = 30
```

## Monitoring and Reporting

### Log Format
```json
{
  "timestamp": "ISO8601",
  "event_type": "goal_submission|hypothesis_generation|pattern_alert",
  "content_hash": "SHA256",
  "metadata": {},
  "trust_level": "string",
  "user_id": "string"
}
```

### Report Generation
- Daily summary reports
- Weekly pattern analysis
- Monthly audit trails
- On-demand exports

## Migration from Heavy-Handed System

For systems migrating from the original safety specification:
1. Existing SafetyLevel and SafetyCheck models remain compatible
2. Safety scores default to high values (0.9-1.0)
3. All decisions default to SAFE unless LLM refuses
4. Review requirements become advisory logs

## Examples

### Example 1: Research Goal Logging
```json
{
  "input": "Study protein folding in neurodegenerative diseases",
  "output": {
    "decision": "SAFE",
    "safety_score": 1.0,
    "reasoning": "Research goal logged",
    "log_id": "2024-01-18-001"
  }
}
```

### Example 2: Trust Level Override
```json
{
  "config_override": {
    "domain": "antimicrobial_resistance",
    "trust_level": "trusted",
    "reason": "Legitimate research domain"
  }
}
```

### Example 3: Pattern Report
```json
{
  "weekly_report": {
    "total_goals": 47,
    "total_hypotheses": 312,
    "patterns": ["Consistent focus on drug discovery"],
    "concerns": "None identified"
  }
}
```

## Future Enhancements

The lightweight system can be enhanced with:
- Machine learning for pattern recognition
- Integration with institutional review systems
- Automated report generation
- API for external monitoring tools

## Comparison with Original System

| Feature | Original | Lightweight |
|---------|----------|-------------|
| Hard blocking | Yes | No |
| Complex evaluation | Yes | No |
| User trust levels | No | Yes |
| Easy disable | No | Yes |
| Performance impact | High | Minimal |
| False positives | Likely | Rare |

The lightweight approach prioritizes usability and research freedom while maintaining accountability through comprehensive logging.