import { useRef, useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { ChevronDown, Check, Info } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { setDuration, setTimeStep, setOutputFrequency } from '../../redux/slices/conditionsSlice'
import { useClickOutside } from '../../hooks/useClickOutside'
import { TIME_RANGE_UNITS } from '../Plots/timeRangeUnits'

// Matches the species name input on the Mechanism page's Species tab: a gray-ringed,
// gray-text field with no native number spinner arrows.
const NUMBER_INPUT =
  'w-72 h-9 px-2 border border-gray-400 bg-white/10 text-gray-900 placeholder:text-gray-500 rounded-lg text-sm text-center font-mono focus:outline-none focus:border-green-700 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none'

// Unit dropdown sitting to the left of a field's input, sharing the same TIME_RANGE_UNITS
// (hours/seconds) used by the Flux tab's time range picker.
function UnitDropdown({ unitId, onChange }) {
  const [open, setOpen] = useState(false)
  const menuRef = useRef(null)
  useClickOutside(menuRef, () => setOpen(false), open)

  const unit = TIME_RANGE_UNITS.find((u) => u.id === unitId) ?? TIME_RANGE_UNITS[0]

  return (
    <div className="relative flex-shrink-0 w-72" ref={menuRef}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 w-full h-9 px-2 border border-gray-300 rounded-lg text-sm text-gray-800 hover:bg-gray-50"
      >
        <ChevronDown className="w-3.5 h-3.5 flex-shrink-0 invisible" />
        <span className="flex-1 text-center">{unit.label}</span>
        <ChevronDown className="w-3.5 h-3.5 flex-shrink-0" />
      </button>

      {open && (
        <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg py-1">
          {TIME_RANGE_UNITS.map((u) => (
            <button
              key={u.id}
              type="button"
              onClick={() => {
                onChange(u.id)
                setOpen(false)
              }}
              className="w-full flex items-center gap-2 text-left text-sm px-3 py-1.5 text-gray-800 hover:bg-gray-100"
            >
              <Check
                className={`w-3.5 h-3.5 flex-shrink-0 ${
                  unitId === u.id ? 'opacity-100' : 'opacity-0'
                }`}
              />
              {u.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function getDivisor(unitId) {
  return (TIME_RANGE_UNITS.find((u) => u.id === unitId) ?? TIME_RANGE_UNITS[0]).divisor
}

/**
 * BasicConfigTab Component
 * Manages basic simulation configuration (duration, timestep, output frequency)
 */
export function BasicConfigTab() {
  const dispatch = useDispatch()
  const basic = useSelector((state) => state.conditions.basic)

  const [durationUnitId, setDurationUnitId] = useState('hours')
  const [timeStepUnitId, setTimeStepUnitId] = useState('seconds')
  const [outputFrequencyUnitId, setOutputFrequencyUnitId] = useState('seconds')

  const durationDivisor = getDivisor(durationUnitId)
  const timeStepDivisor = getDivisor(timeStepUnitId)
  const outputFrequencyDivisor = getDivisor(outputFrequencyUnitId)

  const handleDurationChange = (e) => {
    const value = parseFloat(e.target.value)
    if (!isNaN(value)) {
      dispatch(setDuration(value * durationDivisor))
    }
  }

  const handleTimeStepChange = (e) => {
    const value = parseFloat(e.target.value)
    if (!isNaN(value)) {
      dispatch(setTimeStep(value * timeStepDivisor))
    }
  }

  const handleOutputFrequencyChange = (e) => {
    const value = parseFloat(e.target.value)
    if (!isNaN(value)) {
      dispatch(setOutputFrequency(value * outputFrequencyDivisor))
    }
  }

  return (
    <div className="w-fit mx-auto space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Simulation Time</CardTitle>
          <CardDescription>Configure how long the simulation runs and its temporal resolution</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="w-72 mx-auto">
            <label className="block text-base font-semibold text-gray-900 mb-2">
              Simulation time
            </label>
            <div className="flex flex-col gap-2">
              <UnitDropdown unitId={durationUnitId} onChange={setDurationUnitId} />
              <input
                type="number"
                value={basic.duration / durationDivisor}
                onChange={handleDurationChange}
                step="any"
                min="0"
                className={NUMBER_INPUT}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Set how long you want the simulation to run
            </p>
          </div>

          <div className="w-72 mx-auto">
            <label className="block text-base font-semibold text-gray-900 mb-2">
              Time step
            </label>
            <div className="flex flex-col gap-2">
              <UnitDropdown unitId={timeStepUnitId} onChange={setTimeStepUnitId} />
              <input
                type="number"
                value={basic.timeStep / timeStepDivisor}
                onChange={handleTimeStepChange}
                step="any"
                min="1"
                className={NUMBER_INPUT}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Set the time interval between steps
            </p>
          </div>

          <div className="w-72 mx-auto">
            <label className="block text-base font-semibold text-gray-900 mb-2">
              Output time step
            </label>
            <div className="flex flex-col gap-2">
              <UnitDropdown unitId={outputFrequencyUnitId} onChange={setOutputFrequencyUnitId} />
              <input
                type="number"
                value={basic.outputFrequency / outputFrequencyDivisor}
                onChange={handleOutputFrequencyChange}
                step="any"
                min="1"
                className={NUMBER_INPUT}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Save output every {basic.outputFrequency} seconds
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-lg p-3 text-xs text-gray-700">
        <p className="font-semibold mb-1 flex items-center gap-2">
          <Info className="w-4 h-4" />
          Summary:
        </p>
        <ul className="space-y-0.5 ml-4">
          <li>• Total steps: {Math.floor(basic.duration / basic.timeStep)}</li>
          <li>
            • Output points: {Math.floor(basic.duration / basic.outputFrequency) + 1}
          </li>
          <li>• Simulation end time: {(basic.duration / 3600).toFixed(2)} hours</li>
        </ul>
      </div>
    </div>
  )
}

export default BasicConfigTab
