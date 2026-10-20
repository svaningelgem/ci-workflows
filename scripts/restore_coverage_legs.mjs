// Restore every pytest leg's coverage data from the cache: actions/cache/restore takes a single key.
import { restoreCache } from '@actions/cache'

export default async function restoreLegs({ core, context }) {
  for (const os of JSON.parse(process.env.OSES)) {
    for (const python of JSON.parse(process.env.PYTHONS)) {
      // The newest attempt's entry: a leg that passed is not re-run with the ones that failed.
      const leg = `coverage-${context.runId}-${os}-${python}-`
      if (!(await restoreCache([process.env.LEGS_PATH], `${leg}${process.env.GITHUB_RUN_ATTEMPT}`, [leg], {}, true))) {
        core.warning(`No coverage data from ${os}${python && `, ${python}`}`)
      }
    }
  }
}
