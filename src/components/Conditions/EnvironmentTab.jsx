import { useSelector, useDispatch } from 'react-redux'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { setTemperature, setPressure } from '../../redux/slices/conditionsSlice'

/**
 * EnvironmentTab Component
 * Manages environmental conditions (temperature, pressure)
 */
export function EnvironmentTab() {
  const dispatch = useDispatch()
  const initial = useSelector((state) => state.conditions.initial)

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Environmental Conditions</CardTitle>
          <CardDescription>Set initial temperature and pressure</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-blue-900 mb-2">
              Temperature (K)
            </label>
            <input
              type="number"
              value={initial.temperature}
              onChange={(e) => {
                const value = parseFloat(e.target.value)
                if (!isNaN(value)) dispatch(setTemperature(value))
              }}
              step="0.1"
              min="0"
              className="w-full px-3 py-2 border-2 border-white/30 bg-white/10 text-gray-900 placeholder:text-gray-500 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              {(initial.temperature - 273.15).toFixed(2)}°C
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-blue-900 mb-2">Pressure (Pa)</label>
            <input
              type="number"
              value={initial.pressure}
              onChange={(e) => {
                const value = parseFloat(e.target.value)
                if (!isNaN(value)) dispatch(setPressure(value))
              }}
              step="100"
              min="0"
              className="w-full px-3 py-2 border-2 border-white/30 bg-white/10 text-gray-900 placeholder:text-gray-500 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              {(initial.pressure / 101325).toFixed(4)} atm
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default EnvironmentTab
