# Context Optimization - How to Enable/Disable

Context optimization helps reduce memory usage and improve performance by intelligently selecting the most relevant papers and memories for AI agents, instead of using all available context.

## 🚨 Current Status: DISABLED by Default

Context optimization is currently **disabled by default** for safety and testing purposes.

## 🔧 Quick Enable/Disable

### Method 1: Simple File Toggle (Recommended)

```bash
# Enable context optimization
touch .context_optimization_enabled

# Disable context optimization
touch .context_optimization_disabled

# Remove both files to use environment variable settings
rm .context_optimization_enabled .context_optimization_disabled
```

### Method 2: Environment Variables

```bash
# Enable context optimization
export CONTEXT_OPTIMIZATION_ENABLED=true

# Disable context optimization
export CONTEXT_OPTIMIZATION_ENABLED=false
```

### Method 3: Aggressive Mode (Advanced Users)

```bash
# Enable aggressive optimization (more filtering, lower confidence thresholds)
touch .context_optimization_aggressive
```

## 📊 Check Current Status

```python
from src.utils.context_optimization_runtime import ContextOptimizationRuntimeControl

runtime = ContextOptimizationRuntimeControl()
print(runtime.get_status_report())
```

## ⚙️ Advanced Configuration

### Fine-tune Optimization Settings

```bash
# Set confidence threshold (0.0 to 1.0, default: 0.8)
export CONTEXT_OPTIMIZATION_CONFIDENCE_THRESHOLD=0.7

# Set maximum papers to include (default: 8)
export LITERATURE_MAX_PAPERS=10

# Set maximum memory entries (default: 10)
export MEMORY_MAX_ENTRIES=15

# Auto-enable when context exceeds token limit (default: 100000)
export CONTEXT_OPTIMIZATION_AUTO_THRESHOLD=50000
```

### Disable Specific Features

```bash
# Disable literature optimization only
export LITERATURE_OPTIMIZATION_ENABLED=false

# Disable memory optimization only
export MEMORY_OPTIMIZATION_ENABLED=false

# Disable output validation
export OUTPUT_VALIDATION_ENABLED=false
```

## 🔍 Monitor Optimization

View metrics and effectiveness:

```bash
# Check if any optimizations have run
ls .context_optimization_metrics.log

# View recent optimization activity
tail .context_optimization_metrics.log
```

## 🚀 Future CLI Integration

When the Natural Language Interface (Phase 16) is complete, you'll be able to toggle optimization with simple commands:

```bash
# Future CLI commands (not yet implemented)
./ai-scientist config set context-optimization enabled
./ai-scientist config set context-optimization disabled
./ai-scientist config show context-optimization
./ai-scientist optimize --aggressive
```

## 🛡️ Safety Features

- **Automatic fallback**: If optimization confidence is low, system automatically uses full context
- **Quality validation**: Agent outputs are validated when using optimized context
- **Conservative defaults**: System errs on the side of caution
- **Metrics logging**: All optimizations are logged for analysis

## 🎯 When to Enable

**Enable when:**
- Working with large literature databases (>20 papers)
- Memory usage is high
- Processing is slow
- You have many research iterations

**Keep disabled when:**
- You need maximum accuracy
- Working on critical research
- Testing new features
- Uncertain about optimization impact

## 📈 Expected Benefits

When enabled, you should see:
- **Faster processing**: Less context to process
- **Lower memory usage**: Reduced token counts
- **Maintained quality**: Smart selection preserves important information
- **Better performance**: Especially with large context windows

## 🔧 Troubleshooting

**Optimization not working?**
1. Check if `.context_optimization_disabled` file exists
2. Verify environment variables: `echo $CONTEXT_OPTIMIZATION_ENABLED`
3. Check logs for confidence threshold issues
4. Run status report to see current configuration

**Quality concerns?**
1. Increase confidence threshold: `export CONTEXT_OPTIMIZATION_CONFIDENCE_THRESHOLD=0.9`
2. Increase max papers/memories limits
3. Monitor fallback rate in metrics
4. Consider disabling for critical tasks