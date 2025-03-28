module.exports = {
  onPreBuild: async ({ utils }) => {
    try {
      console.log('Installing system dependencies for Python packages...');
      await utils.run.command('apt-get update && apt-get install -y python3-dev build-essential libssl-dev libffi-dev');
      console.log('System dependencies installed successfully');
    } catch (error) {
      console.log('Error installing system dependencies:', error);
      // Don't fail the build if this step fails
    }
  }
}