import { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Toggle } from '../ui/toggle'
import { useToast } from '@/hooks/use-toast'
import {
  setEvolvingEnabled,
  setEvolvingTimes,
  setEvolvingTemperature,
  setEvolvingPressure,
  setEvolvingAdditionalSeries,
} from '../../redux/slices/conditionsSlice'
import { UnitDropdown } from '../Plots/UnitDropdown'
import { TIME_RANGE_UNITS } from '../Plots/timeRangeUnits'
import { TEMPERATURE_UNITS, toKelvin, fromKelvin } from '../Plots/temperatureUnits'
import { PRESSURE_UNITS } from '../Plots/pressureUnits'
import { DENSITY_UNITS } from '../Plots/densityUnits'
import { LIST_CARD, LIST_CARD_CONTENT, FIELD_LABEL } from '../Mechanism/fieldStyles'

// Air density is optional, so its values live in the evolving slice's generic
// additionalSeries map (the same place hidden series like PHOTO.* are kept) instead of
// getting a dedicated array field.
const DENSITY_SERIES_KEY = 'AIR.density.kg_m3'

// Unlike the Species editor's equal-width columns, the left column here shrinks to its
// content (matching TimeTab) and the right column grows to take up the freed space.
const EDITOR_GRID = 'grid grid-cols-1 gap-4 lg:grid-cols-[auto_1fr] lg:items-start'

// Matches TimeTab's field sizing so both tabs' dropdown/input boxes line up.
const NUMBER_INPUT =
  'w-72 h-9 px-2 border border-gray-400 bg-white/10 text-gray-900 placeholder:text-gray-500 rounded-lg text-sm text-center font-mono focus:outline-none focus:border-green-700 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none'

const DROPDOWN_WRAPPER = 'relative w-72 flex-shrink-0'
const DROPDOWN_BUTTON =
  'flex items-center gap-1 w-full h-9 px-2 border border-gray-300 rounded-lg text-sm text-gray-800 hover:bg-gray-50'

function getUnit(units, unitId) {
  return units.find((u) => u.id === unitId) ?? units[0]
}

function insertAdditionalSeriesValue(series, insertIndex, value = null) {
  return Object.fromEntries(
    Object.entries(series || {}).map(([name, values]) => {
      const nextValues = Array.isArray(values) ? [...values] : []
      nextValues.splice(insertIndex, 0, value)
      return [name, nextValues]
    })
  )
}

function removeAdditionalSeriesValue(series, removeIndex) {
  return Object.fromEntries(
    Object.entries(series || {}).map(([name, values]) => [
      name,
      (Array.isArray(values) ? values : []).filter((_, index) => index !== removeIndex),
    ])
  )
}

/**
 * EnvironmentTab Component
 * Editor + list for time-varying environment conditions (time, temperature, pressure)
 */
export function EnvironmentTab() {
  const dispatch = useDispatch()
  const { toast } = useToast()
  const evolving = useSelector((state) => state.conditions.evolving)

  const [unitIds, setUnitIds] = useState({
    time: 'seconds',
    temperature: 'K',
    pressure: 'Pa',
    density: 'kg_m3',
  })
  const [newTime, setNewTime] = useState('')
  const [newTemperature, setNewTemperature] = useState('')
  const [newPressure, setNewPressure] = useState('')
  const [densityEnabled, setDensityEnabled] = useState(false)
  const [newDensity, setNewDensity] = useState('')

  const handleAdd = () => {
    if (!newTime || !newTemperature || !newPressure || (densityEnabled && !newDensity)) {
      toast({
        title: 'Missing Fields',
        description: densityEnabled
          ? 'Please fill in time, temperature, pressure, and air density values'
          : 'Please fill in time, temperature, and pressure values',
        variant: 'destructive',
      })
      return
    }

    const rawTime = parseFloat(newTime)
    const rawTemperature = parseFloat(newTemperature)
    const rawPressure = parseFloat(newPressure)
    const rawDensity = densityEnabled ? parseFloat(newDensity) : null

    if (
      isNaN(rawTime) ||
      isNaN(rawTemperature) ||
      isNaN(rawPressure) ||
      (densityEnabled && isNaN(rawDensity))
    ) {
      toast({
        title: 'Invalid Input',
        description: 'All values must be valid numbers',
        variant: 'destructive',
      })
      return
    }

    const timeUnit = getUnit(TIME_RANGE_UNITS, unitIds.time)
    const pressureUnit = getUnit(PRESSURE_UNITS, unitIds.pressure)
    const densityUnit = getUnit(DENSITY_UNITS, unitIds.density)

    const time = rawTime * timeUnit.divisor
    const temperature = toKelvin(rawTemperature, unitIds.temperature)
    const pressure = rawPressure * pressureUnit.divisor
    const density = densityEnabled ? rawDensity * densityUnit.divisor : null

    if (evolving.times.includes(time)) {
      toast({
        title: 'Duplicate Time Point',
        description: `A condition already exists at t=${rawTime}${timeUnit.label}`,
        variant: 'destructive',
      })
      return
    }

    const newTimes = [...evolving.times, time].sort((a, b) => a - b)
    const insertIndex = newTimes.indexOf(time)

    const newTemps = [...evolving.temperature]
    newTemps.splice(insertIndex, 0, temperature)

    const newPresses = [...evolving.pressure]
    newPresses.splice(insertIndex, 0, pressure)

    let newAdditionalSeries = insertAdditionalSeriesValue(evolving.additionalSeries, insertIndex)

    if (densityEnabled) {
      const existingDensitySeries = Array.isArray(evolving.additionalSeries?.[DENSITY_SERIES_KEY])
        ? evolving.additionalSeries[DENSITY_SERIES_KEY]
        : new Array(evolving.times.length).fill(null)
      const nextDensitySeries = [...existingDensitySeries]
      nextDensitySeries.splice(insertIndex, 0, density)
      newAdditionalSeries = { ...newAdditionalSeries, [DENSITY_SERIES_KEY]: nextDensitySeries }
    }

    dispatch(setEvolvingEnabled(true))
    dispatch(setEvolvingTimes(newTimes))
    dispatch(setEvolvingTemperature(newTemps))
    dispatch(setEvolvingPressure(newPresses))
    dispatch(setEvolvingAdditionalSeries(newAdditionalSeries))

    toast({
      title: 'Condition Added',
      description: `Added condition at t=${rawTime}${timeUnit.label}`,
      variant: 'success',
    })

    setNewTime('')
    setNewTemperature('')
    setNewPressure('')
    setNewDensity('')
  }

  const handleRemove = (index) => {
    const removedTime = evolving.times[index]
    const newTimes = evolving.times.filter((_, i) => i !== index)
    const newTemps = evolving.temperature.filter((_, i) => i !== index)
    const newPresses = evolving.pressure.filter((_, i) => i !== index)
    const newAdditionalSeries = removeAdditionalSeriesValue(evolving.additionalSeries, index)

    dispatch(setEvolvingTimes(newTimes))
    dispatch(setEvolvingTemperature(newTemps))
    dispatch(setEvolvingPressure(newPresses))
    dispatch(setEvolvingAdditionalSeries(newAdditionalSeries))

    toast({
      title: 'Condition Removed',
      description: `Removed condition at t=${removedTime}s`,
      variant: 'delete',
    })
  }

  return (
    <div className={EDITOR_GRID}>
      <Card className="w-fit">
        <CardHeader>
          <CardTitle>Environment condition</CardTitle>
          <CardDescription>Set temperature and pressure, with optional air density</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="w-72 mx-auto">
            <label className={FIELD_LABEL}>Time</label>
            <div className="flex flex-col gap-2">
              <UnitDropdown
                unitId={unitIds.time}
                onChange={(id) => setUnitIds((prev) => ({ ...prev, time: id }))}
                units={TIME_RANGE_UNITS}
                wrapperClassName={DROPDOWN_WRAPPER}
                buttonClassName={DROPDOWN_BUTTON}
                centerLabel
              />
              <input
                type="text"
                inputMode="decimal"
                value={newTime}
                onChange={(e) => setNewTime(e.target.value)}
                placeholder="0"
                className={NUMBER_INPUT}
              />
            </div>
          </div>

          <div className="w-72 mx-auto">
            <label className={FIELD_LABEL}>Temperature</label>
            <div className="flex flex-col gap-2">
              <UnitDropdown
                unitId={unitIds.temperature}
                onChange={(id) => setUnitIds((prev) => ({ ...prev, temperature: id }))}
                units={TEMPERATURE_UNITS}
                wrapperClassName={DROPDOWN_WRAPPER}
                buttonClassName={DROPDOWN_BUTTON}
                centerLabel
              />
              <input
                type="text"
                inputMode="decimal"
                value={newTemperature}
                onChange={(e) => setNewTemperature(e.target.value)}
                placeholder="298.15"
                className={NUMBER_INPUT}
              />
            </div>
          </div>

          <div className="w-72 mx-auto">
            <label className={FIELD_LABEL}>Pressure</label>
            <div className="flex flex-col gap-2">
              <UnitDropdown
                unitId={unitIds.pressure}
                onChange={(id) => setUnitIds((prev) => ({ ...prev, pressure: id }))}
                units={PRESSURE_UNITS}
                wrapperClassName={DROPDOWN_WRAPPER}
                buttonClassName={DROPDOWN_BUTTON}
                centerLabel
              />
              <input
                type="text"
                inputMode="decimal"
                value={newPressure}
                onChange={(e) => setNewPressure(e.target.value)}
                placeholder="101325"
                className={NUMBER_INPUT}
              />
            </div>
          </div>

          <div className="w-72 mx-auto">
            <Toggle
              checked={densityEnabled}
              label="Air density"
              onChange={setDensityEnabled}
              size="sm"
            />
            {densityEnabled && (
              <div className="mt-2 flex flex-col gap-2">
                <UnitDropdown
                  unitId={unitIds.density}
                  onChange={(id) => setUnitIds((prev) => ({ ...prev, density: id }))}
                  units={DENSITY_UNITS}
                  wrapperClassName={DROPDOWN_WRAPPER}
                  buttonClassName={DROPDOWN_BUTTON}
                  centerLabel
                />
                <input
                  type="text"
                  inputMode="decimal"
                  value={newDensity}
                  onChange={(e) => setNewDensity(e.target.value)}
                  placeholder="1.225"
                  className={NUMBER_INPUT}
                />
              </div>
            )}
          </div>
          <div className="h-0.5"/>
          <div className="mt-8 flex justify-center">
            <Button
              onClick={handleAdd}
              variant="assistSecondary"
              className="h-9 px-8 text-base">
              Add condition
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className={LIST_CARD}>
        <CardHeader>
          <CardTitle>{evolving.times.length} condition{evolving.times.length === 1 ? '' : 's'}</CardTitle>
          <CardDescription>Conditions added, sorted by time</CardDescription>
        </CardHeader>
        <CardContent className={LIST_CARD_CONTENT}>
          {evolving.times.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No conditions added. Add your first condition on the left.
            </p>
          ) : (
            <div className="space-y-2 overflow-y-auto">
              {evolving.times.map((time, index) => {
                const densitySeries = evolving.additionalSeries?.[DENSITY_SERIES_KEY]
                const density = densitySeries?.[index]
                const hasDensityColumn = Array.isArray(densitySeries) && densitySeries.some((v) => v != null)

                return (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-3 border border-white/20 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                  >
                    <div
                      className={`flex-1 grid ${hasDensityColumn ? 'grid-cols-4' : 'grid-cols-3'} gap-2 text-sm font-mono`}
                    >
                      <div>{time}s</div>
                      <div>
                        {evolving.temperature[index]}K
                        <span className="text-xs text-gray-500 ml-1">
                          ({fromKelvin(evolving.temperature[index], 'C').toFixed(1)}°C)
                        </span>
                      </div>
                      <div>
                        {evolving.pressure[index]}Pa
                        <span className="text-xs text-gray-500 ml-1">
                          ({(evolving.pressure[index] / 101325).toFixed(2)} atm)
                        </span>
                      </div>
                      {hasDensityColumn && <div>{density != null ? `${density} kg/m³` : '—'}</div>}
                    </div>
                    <Button
                      variant="glass"
                      size="sm"
                      onClick={() => handleRemove(index)}
                      className="rounded-lg text-red-600 hover:bg-red-900/20 backdrop-blur-lg"
                    >
                      Remove
                    </Button>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default EnvironmentTab
